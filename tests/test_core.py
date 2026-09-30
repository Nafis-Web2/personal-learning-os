def test_weights_sum():
    from app.services.mastery import WEIGHTS
    assert abs(sum(WEIGHTS.values())-1.0) < 1e-9

def test_curricula_have_depth():
    from app.seed.curricula import PYTHON, TRADING
    assert len(PYTHON)==14
    assert len(TRADING)==13
    assert sum(len(x[2]) for x in PYTHON) > 60
