import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scan_build_paths import scan  # noqa: E402


def nested_apk(path, inner_files):
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, 'w') as archive:
        for name, data in inner_files.items():
            archive.writestr(name, data)
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('assets/chaquopy/requirements-common.imy', inner.getvalue())
        archive.writestr('classes.dex', b'\x00dex')


def test_nested_member_is_found_and_account_is_redacted(tmp_path):
    apk = tmp_path / 'app.apk'
    nested_apk(apk, {'pkg/sbom.json': b'path+file:///var/home/qa-account/build/src',
                     'pkg/_ext.so': b'\x7fELF /home/qa-account/.cargo/registry/src/x.rs'})
    findings = scan([apk])
    labels = sorted(findings)
    assert labels == [f'{apk}!assets/chaquopy/requirements-common.imy!pkg/_ext.so',
                      f'{apk}!assets/chaquopy/requirements-common.imy!pkg/sbom.json']
    # The account learnt from /var/home is also searched as /home/<account>.
    assert all('qa-account' not in value for values in findings.values() for value in values)


def test_checkout_path_and_strict_mode(tmp_path):
    apk = tmp_path / 'app.apk'
    nested_apk(apk, {'core.dist-info/direct_url.json': b'{"url": "file:///X:/Work/checkout/vendor/core.whl"}',
                     'numpy/_datasource.pyc': b'/home/upstream/docs'})
    default = scan([apk], extra=['X:\\Work\\checkout'])
    assert list(default) == [f'{apk}!assets/chaquopy/requirements-common.imy!core.dist-info/direct_url.json']
    strict = scan([apk], strict=True)
    assert f'{apk}!assets/chaquopy/requirements-common.imy!numpy/_datasource.pyc' in strict


def test_clean_wheel(tmp_path):
    wheel = tmp_path / 'pkg-1.0-py3-none-any.whl'
    with zipfile.ZipFile(wheel, 'w') as archive:
        archive.writestr('pkg/__init__.py', 'PATH = "/build/src/pkg"\n')
    assert scan([wheel], strict=True) == {}
