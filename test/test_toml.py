import pathlib

from  mdfile.main import load_mdfile_config
def test_load_toml_1():
    """Second case with different values ...just to be sure"""
    toml_file = pathlib.Path('toml/main/dir1/dir2/pyproject.toml')
    cfg = load_mdfile_config(toml_file)

    assert cfg['output'] == "output1.md"
    assert cfg['file_name'] == "input1.mdd"
    assert cfg['auto_break'] == True
    assert cfg['plain'] == False
    assert cfg['vars_file'] == "vars_file1.json"

def test_load_toml_2():
    """Second case with different values ...just to be sure"""
    toml_file = pathlib.Path('toml/main/dir1/pyproject.toml')
    cfg = load_mdfile_config(toml_file)

    assert cfg['output'] == 'output_2.md'
    assert cfg['file_name'] == "input_2.mdd"
    assert cfg['auto_break'] == True
    assert cfg['plain'] == False
    assert cfg['vars_file'] == "vars_file2.json"


def test_load_toml_1_deep():
    """Second case with different values ...just to be sure"""
    toml_file = pathlib.Path.cwd() / 'toml/main/dir1/dir2/pp_1.toml'
    assert toml_file.exists()
    cfg = load_mdfile_config(toml_file)

    assert cfg['output'] == "output1.md"
    assert cfg['file_name'] == "input1.mdd"
    assert cfg['auto_break'] == True
    assert cfg['plain'] == False
    assert cfg['vars_file'] == "vars_file1.json"