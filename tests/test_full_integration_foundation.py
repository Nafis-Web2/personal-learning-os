from app.intelligence.integrated import validate_evidence,next_learning_action,retention_interval,trading_process,personalization

def test_full_solution_does_not_count_as_mastery():
    assert not validate_evidence('x',{'application':100},6)['eligible']

def test_priority_order():
    assert next_learning_action(repair=True,daily_gate=True,retention=True,application=True,current_lesson=True)=='repair'
    assert next_learning_action(retention=True,application=True,current_lesson=True)=='retention_review'

def test_retention_adapts():
    assert retention_interval(90,90,7)==14
    assert retention_interval(50,100,7)==3

def test_profit_not_process():
    x=trading_process(90,30,90,40,90,500,2)
    assert x['profitable'] and x['readiness_credit']<70

def test_personalization_keeps_standard():
    x=personalization(history=[{'score':50,'help_level':4}]*6)
    assert x['mastery_standards_changed'] is False

def test_persistent_integration_models_exist():
    from app.models import PersonalizationSnapshot,ApplicationAttempt
    assert PersonalizationSnapshot.__tablename__=='personalization_snapshots'
    assert ApplicationAttempt.__tablename__=='application_attempts'

def test_today_route_uses_real_orm_fields():
    import inspect
    from app.main import integrated_today
    src=inspect.getsource(integrated_today)
    assert "status='open'" in src
    assert "active=True" in src
    assert "status='active'" not in src
