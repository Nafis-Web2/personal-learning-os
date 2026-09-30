from dataclasses import dataclass

HELP_CAP={0:100,1:95,2:85,3:75,4:60,5:40,6:0}

@dataclass
class TeacherTurn:
    mode:str
    message:str
    help_level:int=0
    action:str='respond'

def validate_evidence(concept_id:str,dimensions:dict,help_level:int=0,observable:bool=True):
    if not observable:return {'eligible':False,'reason':'observable performance required'}
    if help_level>=6:return {'eligible':False,'reason':'fresh retest required','needs_fresh_retest':True}
    allowed={'recall','understanding','application','transfer','independence','retention'}
    clean={k:max(0,min(100,float(v))) for k,v in dimensions.items() if k in allowed}
    if 'independence' in clean:clean['independence']=min(clean['independence'],HELP_CAP[help_level])
    return {'eligible':bool(clean),'concept_id':concept_id,'dimensions':clean,'help_level':help_level}

def next_learning_action(*,proof=False,repair=False,daily_gate=False,retention=False,application=False,current_lesson=False):
    for flag,kind in [(proof,'prove_i_know_it'),(repair,'repair'),(daily_gate,'daily_gate'),(retention,'retention_review'),(application,'application'),(current_lesson,'lesson')]:
        if flag:return kind
    return 'choose'

def teacher_turn(mode:str,topic:str,help_level:int=0):
    if mode in {'assessment','daily_gate','cold_test','weekly_synthesis'}:help_level=0
    prompts={
      'diagnose':f'Before I teach {topic}, explain what you already know about it.',
      'teach':f'Let’s build {topic} from the core idea, then you will apply it yourself.',
      'repair':f'Let’s isolate the exact gap in {topic}, repair it, then retest with a fresh problem.',
      'practice':f'Try a fresh {topic} problem. I will not reveal the solution unless the help ladder requires it.',
      'assessment':f'Explain and apply {topic} without hints.',
    }
    return TeacherTurn(mode=mode,message=prompts.get(mode,f'Work on {topic}.'),help_level=help_level)

def retention_interval(score:float,independence:float,current_days:int=1):
    if score>=85 and independence>=75:return min(120,max(3,current_days*2))
    if score<70:return max(1,current_days//2)
    return current_days

def application_score(correctness,reasoning,adaptation,independence):
    return round(correctness*.35+reasoning*.25+adaptation*.25+independence*.15,1)

def trading_process(plan,risk,execution,discipline,review,pnl,rule_breaks=0):
    process=round(plan*.20+risk*.30+execution*.20+discipline*.20+review*.10,1)
    return {'process_score':process,'readiness_credit':round(max(0,process-rule_breaks*10),1),'pnl':pnl,'profitable':pnl>0}

def personalization(*,history:list,preferred='visual',current_difficulty=2):
    if len(history)<5:return {'strategy':preferred,'difficulty':current_difficulty,'max_help_level':4,'confidence':'low','mastery_standards_changed':False}
    recent=history[-8:];avg=sum(float(x.get('score',0)) for x in recent)/len(recent);assist=sum(int(x.get('help_level',0))>=2 for x in recent)/len(recent)
    diff=min(5,current_difficulty+1) if avg>=88 and assist<=.25 else max(1,current_difficulty-1) if avg<65 else current_difficulty
    return {'strategy':preferred,'difficulty':diff,'max_help_level':2 if assist>=.65 else 3 if assist>=.4 else 4,'confidence':'medium' if len(history)<20 else 'high','mastery_standards_changed':False}
