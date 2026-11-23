"""Run the separate 12-graph exploratory plan with resumable process evidence."""

import argparse
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import UTC, datetime
import os
from pathlib import Path
import shutil
import signal
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cli.campaign_evidence import atomic_json, audit_attempt, file_hash, summarize
from src.cli.campaign_system import awake, exclusive_lock, observation
from src.cli.distributed_campaign import _identity, _saved_rows, execute_attempt
from src.cli.distributed_plan import attempt_keys, attempt_name, digest, read_json, runtime, source_inventory
from src.cli.variants import VARIANTS
from src.graphs import load_fhcp_graph


def physical_cpus(count):
    """Choose one logical CPU per physical core, avoiding sibling threads."""
    if not hasattr(os, 'sched_getaffinity'):
        raise ValueError('Este ejecutador usa afinidad de Linux.')
    cores = {}
    for cpu in sorted(os.sched_getaffinity(0)):
        topology = Path(f'/sys/devices/system/cpu/cpu{cpu}/topology')
        core = tuple((topology / name).read_text().strip()
                     for name in ('physical_package_id', 'core_id'))
        cores.setdefault(core, cpu)
    if len(cores) < count:
        raise ValueError('No hay suficientes núcleos físicos disponibles.')
    return list(cores.values())[:count]


def check_plan(plan):
    if plan['schema'] != 'fhcp-parallel-exploration/1':
        raise ValueError('Formato de plan exploratorio incorrecto.')
    if digest({k: v for k, v in plan.items() if k != 'plan_sha256'}) != plan['plan_sha256']:
        raise ValueError('El hash del plan no coincide.')
    if source_inventory(ROOT) != plan['source_sha256'] or runtime() != plan['runtime']:
        raise ValueError('Cambió el código o el entorno del plan; no mezclar ejecuciones.')
    catalog = ROOT / plan['catalog']['path']
    if not catalog.resolve().is_relative_to(ROOT) or file_hash(catalog) != plan['catalog']['sha256']:
        raise ValueError('Cambió el catálogo de la prueba.')
    if read_json(catalog)['instances'] != plan['instances']:
        raise ValueError('El catálogo y el plan difieren.')
    ids = [e['id'] for e in plan['instances']]
    if len(ids) != len(set(ids)) or plan['assignments'] != {plan['member']: ids}:
        raise ValueError('La asignación debe contener exactamente las instancias seleccionadas.')
    if [s['algorithm'] for s in plan['solvers']] != list(VARIANTS):
        raise ValueError('Se requieren las seis familias del contrato común.')
    for solver in plan['solvers']:
        if VARIANTS[solver['algorithm']].resolve(solver['parameters']) != solver['parameters']:
            raise ValueError('Parámetros no canónicos.')
    if len(set(plan['seeds'])) != len(plan['seeds']) or any(type(s) is not int or not 0 <= s < 2**64 for s in plan['seeds']):
        raise ValueError('Semillas inválidas o repetidas.')
    expected = len(ids) * len(plan['seeds']) * len(plan['solvers'])
    if expected != plan['expected_attempts'] or plan['native_threads'] != 1:
        raise ValueError('Cobertura o número de hilos incorrecto.')
    budget = plan['budget']
    if budget != {'max_elapsed_ns': 30_000_000_000, 'max_evaluations': None, 'max_iterations': None}:
        raise ValueError('Esta prueba requiere 30 segundos sin otro límite de búsqueda.')
    if plan['process_timeout_seconds'] <= 30 or plan['workers_per_machine'] != 4:
        raise ValueError('Límite externo o cantidad de procesos incorrectos.')
    for entry in plan['instances']:
        graph = load_fhcp_graph(entry['id'], root=ROOT, manifest=plan['catalog']['path'])
        del graph


def schedule(keys, saved, cpus, stop_reason, run, record, max_attempts=None):
    """At most one active attempt per graph; drain active work before returning."""
    queues = {}
    for key in keys:
        if key not in saved:
            queues.setdefault(key[0], deque()).append(key)
    idle, active, busy = list(cpus), {}, set()
    admitted, reason = 0, ''
    with ThreadPoolExecutor(max_workers=len(cpus)) as pool:
        while queues or active:
            reason = reason or stop_reason()
            if not reason:
                for graph in list(queues):
                    if not idle:
                        break
                    if max_attempts is not None and admitted >= max_attempts:
                        reason = 'attempt_limit'
                        break
                    if graph in busy:
                        continue
                    cpu = idle.pop(0)
                    key = queues[graph].popleft()
                    if not queues[graph]:
                        del queues[graph]
                    active[pool.submit(run, key, cpu)] = (graph, cpu)
                    busy.add(graph)
                    admitted += 1
            if not active:
                break
            completed, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in completed:
                graph, cpu = active.pop(future)
                busy.remove(graph)
                idle.append(cpu)
                reason = record(future.result()) or reason
    return reason or 'complete'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT / 'experiments/configs/near-miss-12-parallel-10x30.json')
    parser.add_argument('--check', action='store_true', help='Comprobar sin ejecutar algoritmos')
    parser.add_argument('--max-attempts', type=int, help='Pausar tras admitir esta cantidad de intentos nuevos')
    args = parser.parse_args()
    if args.max_attempts is not None and args.max_attempts < 1:
        parser.error('--max-attempts debe ser positivo')
    plan = read_json(args.plan)
    check_plan(plan)
    cpus = physical_cpus(plan['workers_per_machine'])
    output = ROOT / 'experiments/results' / ('near-miss-12-' + plan['campaign_id'])
    print(f"PLAN: {plan['expected_attempts']} intentos; semillas={plan['seeds']}; 30 s; CPUs={cpus}", flush=True)
    print(f'RESULTADOS: {output}', flush=True)
    if args.check:
        print(f'COMPROBACIÓN CORRECTA; recursos={observation()}', flush=True)
        return
    output.mkdir(parents=True, exist_ok=True)
    interrupted = False

    def request_stop(signum, frame):
        nonlocal interrupted
        interrupted = True

    signal.signal(signal.SIGINT, request_stop)
    member = plan['member']
    with exclusive_lock(Path(sys.prefix) / '.fhcp-campaign.lock'), exclusive_lock(output / '.campaign.lock'), awake():
        _identity(plan, member, output, os.uname().nodename, ROOT)
        rows = _saved_rows(plan, member, output, ROOT, recover=True)
        saved = {(r['instance'], r['algorithm'], r['seed']) for r in rows}
        previous, started = len(rows), time.monotonic()
        runner_hash = file_hash(__file__)
        snapshot = output / f'parallel-runner-{runner_hash}.py'
        if not snapshot.exists():
            shutil.copy2(__file__, snapshot)
        summary = summarize(plan, [member], rows, output)
        reason = 'coordinator_error'

        def report(message):
            print(message, flush=True)
            with (output / 'terminal.log').open('a', encoding='utf-8') as stream:
                stream.write(message + '\n')

        def stop_reason():
            if interrupted:
                return 'interrupted'
            if (output / 'STOP').exists():
                return 'stop_file'
            resources = observation()
            if resources['ac_online'] is False:
                return 'ac_disconnected'
            if resources['available_ram_bytes'] is not None and resources['available_ram_bytes'] < 4 * 1024**3:
                return 'low_memory'
            if shutil.disk_usage(output).free < 1024**3:
                return 'low_disk'
            if source_inventory(ROOT) != plan['source_sha256']:
                return 'source_changed'
            return ''

        def run(key, cpu):
            os.sched_setaffinity(0, {cpu})
            directory = output / 'attempts' / attempt_name(key)
            execute_attempt(plan, key, directory, ROOT)
            row = audit_attempt(directory, plan, key, root=ROOT)
            atomic_json(directory / 'audit.json', row)
            return key, row

        def record(result):
            key, row = result
            rows.append(row)
            summarize(plan, [member], rows, output)
            report(f"{len(rows)}/{plan['expected_attempts']} {attempt_name(key)}: {row['status']}; costo={row['best_cost']}; certificado={row['certified_success']}")
            return 'invalid_evidence' if row['stop_reason'] == 'invalid_evidence' else ''

        report(f'INICIO: conservados={previous}; cuatro procesos independientes; CPUs={cpus}')
        try:
            reason = schedule(list(attempt_keys(plan, member)), saved, cpus, stop_reason, run, record, args.max_attempts)
        finally:
            if reason == 'coordinator_error':
                rows = _saved_rows(plan, member, output, ROOT, recover=True)
            summary = summarize(plan, [member], rows, output)
            sessions = output / 'sessions'
            sessions.mkdir(exist_ok=True)
            atomic_json(sessions / (uuid4().hex + '.json'), {
                'at_utc': datetime.now(UTC).isoformat(), 'stop_reason': reason,
                'new_attempts': len(rows) - previous, 'total_attempted': len(rows),
                'session_seconds': time.monotonic() - started, 'execution_mode': 'parallel_exploratory',
                'workers': len(cpus), 'affinity_cpus': cpus, 'runner_sha256': runner_hash,
            })
            report(f"FIN: {reason}; {summary['attempted']}/{summary['planned']}; éxitos={summary['successes']}; grafos certificados={summary['distinct_solved_graphs']}")
    return 0 if summary['attempted'] == summary['planned'] else 3


if __name__ == '__main__':
    sys.exit(main())
