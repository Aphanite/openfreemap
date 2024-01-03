import subprocess
import sys
from pathlib import Path

from http_host_lib import DEFAULT_RUNS_DIR, MNT_DIR, TEMPLATES_DIR


def write_nginx_config():
    with open(TEMPLATES_DIR / 'nginx_cf.conf') as fp:
        nginx_template = fp.read()

    location_str = ''
    curl_text = ''

    for subdir in MNT_DIR.iterdir():
        if not subdir.is_dir():
            continue

        area, version = subdir.name.split('-')

        location_str += create_version_location(area, version, subdir)

        if not curl_text:
            curl_text = (
                '\ntest with:\n'
                f'curl -H "Host: ofm" -I http://localhost/{area}/{version}/14/8529/5975.pbf\n'
                f'curl -I https://tiles.openfreemap.org/{area}/{version}/14/8529/5975.pbf'
            )

    for area in ['monaco', 'planet']:
        location_str += create_latest_location(area)

    nginx_template = nginx_template.replace('___LOCATION_BLOCKS___', location_str)

    with open('/data/nginx/sites/ofm-tiles-org.conf', 'w') as fp:
        fp.write(nginx_template)
        print('  nginx config written')

    subprocess.run(['nginx', '-t'], check=True)
    subprocess.run(['systemctl', 'reload', 'nginx'], check=True)

    print(curl_text)


def create_version_location(area: str, version: str, subdir: Path) -> str:
    run_dir = DEFAULT_RUNS_DIR / area / version
    if not run_dir.is_dir():
        print(f"  {run_dir} doesn't exists, skipping")
        return ''

    tilejson_path = run_dir / 'tilejson-tiles-org.json'

    metadata_path = subdir / 'metadata.json'
    if not metadata_path.is_file():
        print(f"  {metadata_path} doesn't exists, skipping")
        return ''

    url_prefix = f'https://tiles.openfreemap.org/{area}/{version}'

    subprocess.run(
        [
            sys.executable,
            Path(__file__).parent.parent / 'metadata_to_tilejson.py',
            '--minify',
            metadata_path,
            tilejson_path,
            url_prefix,
        ],
        check=True,
    )

    # TODO # target 10y
    return f"""
        location /{area}/{version} {{    # no trailing hash
            alias {tilejson_path};       # no trailing hash
            default_type application/json;

            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header Cache-Control public;
            expires 1d;
        }}

        location /{area}/{version}/ {{    # trailing hash
            alias {subdir}/tiles/;        # trailing hash
            try_files $uri @empty;

            add_header Content-Encoding gzip;
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header Cache-Control public;
            expires 1d;  # target 10y
        }}
    """


def create_latest_location(area: str) -> str:
    local_version_file = Path(f'/data/ofm/config/deployed_tiles_{area}.txt')

    if not local_version_file.exists():
        return ''

    with open(local_version_file) as fp:
        version_str = fp.read().strip()

    print(version_str)