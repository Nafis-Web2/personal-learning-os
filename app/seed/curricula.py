from sqlalchemy.orm import Session
from app.models import Course, Module, Lesson, Concept

PYTHON=[
("P0","Setup & Mental Model",["Running Python","Interpreter and IDE","Syntax errors","Reading tracebacks","Program execution"]),
("P1","Values & Variables",["Numbers","Strings","Booleans","Variables","Assignment","Expressions vs statements"]),
("P2","Operators & Conversion",["Arithmetic","Precedence","Comparison","Logical operators","Type conversion","Augmented assignment"]),
("P3","Strings",["Indexing","Slicing","String methods","Formatting","Escape sequences","Immutability"]),
("P4","Control Flow",["if/elif/else","Truthiness","Nested decisions","Logical conditions"]),
("P5","Loops",["for loops","while loops","range","break and continue","Nested loops","Loop reasoning"]),
("P6","Collections",["Lists","Tuples","Sets","Dictionaries","Nested collections","Choosing collections"]),
("P7","Functions",["Function definition","Parameters and arguments","Return values","Scope","Decomposition","Default and keyword arguments"]),
("P8","Errors & Debugging",["Exceptions","try/except","Validation","Debugging strategies","Reading errors"]),
("P9","Files & Modules",["Text files","Paths","Imports","Modules","Packages","Standard library basics"]),
("P10","OOP Foundations",["Classes","Objects","Attributes","Methods","Constructors","Encapsulation","Composition basics"]),
("P11","Intermediate Python",["Comprehensions","Unpacking","Iterators","Lambda awareness","Useful built-ins","Python patterns"]),
("P12","Testing & Code Quality",["Assertions","Unit-test mindset","Naming","Refactoring","Documentation"]),
("P13","Foundation Projects",["CLI project planning","Combining concepts","Independent debugging","Project explanation"]),]
TRADING=[
("T0","Markets & Instruments",["Stocks","ETFs","Exchanges","Market hours","Market participants"]),
("T1","Trading Styles",["Day trading","Swing trading","Investing","Retail vs institutional/HFT"]),
("T2","Long / Short & Orders",["Long","Short","Bid and ask","Market orders","Limit orders","Stop orders","Slippage"]),
("T3","Volume, Volatility & Liquidity",["Volume","Volatility","Liquidity","Unsuitable conditions"]),
("T4","Catalysts & Premarket Preparation",["News catalysts","Watchlists","Scanners","Gap context","Preparation workflow"]),
("T5","Charts & Price Context",["Candles","Timeframes","Support and resistance","Trend and context"]),
("T6","VWAP & Common Indicators",["VWAP","Indicator limitations","Avoiding indicator dependence"]),
("T7","Risk Management",["Risk per trade","Stop logic","Risk/reward","Position sizing","Daily loss rules"]),
("T8","Setups & Trade Plans",["Setup criteria","Entry","Stop","Target","Invalidation","No-trade conditions"]),
("T9","Execution & Discipline",["Plan adherence","Impulsive entries","Overtrading","Revenge trading"]),
("T10","Journaling & Review",["Trade rationale","Rule adherence","Mistakes","Process metrics"]),
("T11","Simulation",["Historical scenarios","Paper trading","Process evaluation"]),
("T12","Readiness Evaluation",["Sample size","Consistency","Rule adherence","Drawdown and risk review"]),]

def seed_course(db: Session, code, title, modules):
    existing=db.query(Course).filter_by(code=code).first()
    if existing: return existing
    course=Course(code=code,title=title,version=1); db.add(course); db.flush()
    for mi,(mcode,mtitle,concepts) in enumerate(modules):
        m=Module(course_id=course.id,code=mcode,title=mtitle,position=mi); db.add(m); db.flush()
        lesson=Lesson(module_id=m.id,title=mtitle,position=0); db.add(lesson); db.flush()
        for ci,name in enumerate(concepts): db.add(Concept(lesson_id=lesson.id,name=name,position=ci))
    return course

def seed_all(db: Session):
    seed_course(db,"PYTHON_FOUNDATIONS","Python Foundations",PYTHON)
    seed_course(db,"TRADING_FOUNDATIONS","Day Trading Foundations",TRADING)
    db.commit()
    seed_prerequisites(db)

def seed_prerequisites(db: Session):
    # Within each course, each concept depends on the immediately previous concept.
    # This conservative chain can later be replaced by a richer hand-authored graph.
    from app.models import ConceptPrerequisite
    for course in db.query(Course).all():
        concepts=(db.query(Concept).join(Lesson,Concept.lesson_id==Lesson.id).join(Module,Lesson.module_id==Module.id)
                  .filter(Module.course_id==course.id).order_by(Module.position,Lesson.position,Concept.position).all())
        for prev,cur in zip(concepts,concepts[1:]):
            if not db.query(ConceptPrerequisite).filter_by(concept_id=cur.id,prerequisite_concept_id=prev.id).first():
                db.add(ConceptPrerequisite(concept_id=cur.id,prerequisite_concept_id=prev.id))
    db.commit()
