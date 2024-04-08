def test_shell(command):
    stdout, stderr, returncode = command.run('version')
    assert returncode == 0
    assert stdout
    assert not stderr
    assert 'U-Boot' in stdout[0]

    stdout, stderr, returncode = command.run('false')
    assert returncode != 0
    assert not stdout
    assert not stderr
