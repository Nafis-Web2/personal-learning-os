
from sqlalchemy.orm import Session
from app.models import Course,Module,Lesson,Concept,ConceptPrerequisite

PYTHON=[
("P0","Setup & Mental Model",[("Your Python Workspace",["running Python","scripts vs interactive execution","reading errors"])]),
("P1","Values & Variables",[("Values, Types & Variables",["values and types","variables and assignment","naming and reassignment"])]),
("P2","Operators & Conversion",[("Expressions & Operators",["arithmetic operators","operator precedence","augmented assignment"]),("Type Conversion",["int float and string conversion","integer vs float division"])]),
("P3","Strings",[("Working with Strings",["string indexing","string slicing","string methods","escape sequences","formatted strings"])]),
("P4","Control Flow",[("Decisions with if",["boolean expressions","comparison operators","if elif else","truthiness"])]),
("P5","Loops",[("for Loops",["iteration","range","for loop execution"]),("while Loops",["while conditions","loop state","break and continue"])]),
("P6","Collections",[("Lists & Tuples",["lists","list mutation","tuples","sequence unpacking"]),("Sets & Dictionaries",["sets","set membership","dictionaries","dictionary access and iteration"])]),
("P7","Functions",[("Functions",["function definition","parameters and arguments","return values","scope"])]),
("P8","Errors & Debugging",[("Debugging Python",["syntax runtime and logic errors","tracebacks","debugging process","exceptions"])]),
("P9","Files & Modules",[("Files & Modules",["reading and writing files","imports","modules and packages"])]),
("P10","Object-Oriented Python",[("Classes & Objects",["classes and instances","attributes and methods","constructors","encapsulation"])]),
("P11","Intermediate Python",[("Intermediate Patterns",["comprehensions","iterators","higher order functions","decorators basics"])]),
("P12","Testing & Quality",[("Testing & Code Quality",["unit testing","test cases","refactoring","code readability"])]),
("P13","Foundation Projects",[("Independent Python Build",["problem decomposition","implementation","debugging independently","explaining design decisions"])])
]
TRADING=[
("T0","Markets & Instruments",[("Market Foundations",["stocks","ETFs","market participants","bid ask spread"])]),
("T1","Trading Styles",[("Day vs Swing Trading",["day trading","swing trading","time horizon"])]),
("T2","Long, Short & Orders",[("Positions & Orders",["long positions","short positions","market orders","limit orders","stop orders"])]),
("T3","Volume, Volatility & Liquidity",[("Tradeability",["volume","volatility","liquidity","spread quality"])]),
("T4","Catalysts & Premarket",[("Finding Opportunity",["news catalysts","premarket research","relative volume","scanner purpose"])]),
("T5","Charts",[("Price Action Basics",["candlesticks","support and resistance","trend","timeframes"])]),
("T6","VWAP & Indicators",[("VWAP in Context",["VWAP","price versus VWAP","indicator limitations"])]),
("T7","Risk Management",[("Risk Before Reward",["position risk","stop placement","risk reward","position sizing","maximum loss"])]),
("T8","Setups & Plans",[("Trade Planning",["setup criteria","entry plan","invalidation","target plan"])]),
("T9","Execution & Discipline",[("Executing the Plan",["execution discipline","FOMO","rule adherence"])]),
("T10","Journaling",[("Reviewing Trades",["trade journal","process review","mistake classification"])]),
("T11","Simulation",[("Paper Trading",["simulation discipline","sample size","process scoring"])]),
("T12","Readiness",[("Readiness Check",["consistent process","risk adherence","independent trade planning"])])
]

def _seed_course(db,code,title,spec):
    course=db.query(Course).filter_by(code=code).first()
    if course:return course
    course=Course(code=code,title=title,version=1);db.add(course);db.flush()
    prior_last=None
    for mi,(mcode,mtitle,lessons) in enumerate(spec,1):
        mod=Module(course_id=course.id,code=mcode,title=mtitle,position=mi);db.add(mod);db.flush()
        for li,(ltitle,concepts) in enumerate(lessons,1):
            lesson=Lesson(module_id=mod.id,title=ltitle,position=li);db.add(lesson);db.flush()
            local=[]
            for ci,name in enumerate(concepts,1):
                c=Concept(lesson_id=lesson.id,name=name,position=ci);db.add(c);db.flush();local.append(c)
                if prior_last:
                    db.add(ConceptPrerequisite(concept_id=c.id,prerequisite_concept_id=prior_last.id,required_understanding=70,required_application=70))
                prior_last=c
    db.commit();return course

def seed_builtin_curriculum(db:Session):
    return {'python':_seed_course(db,'PYTHON-FOUNDATIONS','Python Foundations',PYTHON),
            'trading':_seed_course(db,'TRADING-FOUNDATIONS','Trading Foundations',TRADING)}
