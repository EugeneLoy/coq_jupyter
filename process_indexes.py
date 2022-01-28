
# TODO find a better way to do this
# This script parses coq tactics\commands index pages and outputs relevant
# keywords to be used in CodeMirror coq mode
# X_data variables are taken from Coq 8.9.0 documentation

commands_data = """
a	
	Abort	
	About	
	Add	
	Add Field	
	Add LoadPath	
	Add ML Path	
	Add Morphism	
	Add Parametric Morphism	
	Add Parametric Relation	
	Add Rec LoadPath	
	Add Relation	
	Add Ring	
	Add Setoid	
	Add Zify	
	Admit Obligations	
	Admitted	
	Arguments	
	Axiom	
	Axioms	
	 	
	b	
	Back	
	BackTo	
	Bind Scope	
	 	
	c	
	Canonical Structure	
	Cd	
	Check	
	Class	
	Close Scope	
	Coercion	
	CoFixpoint	
	CoInductive	
	Collection	
	Combined Scheme	
	Comments	
	Compute	
	Conjecture	
	Conjectures	
	Constraint	
	Context	
	Corollary	
	Create HintDb	
	 	
	d	
	Declare Custom Entry	
	Declare Instance	
	Declare Left Step	
	Declare ML Module	
	Declare Module	
	Declare Morphism	
	Declare Reduction	
	Declare Right Step	
	Declare Scope	
	Defined	
	Definition	
	Delimit Scope	
	Derive	
	Derive Dependent Inversion	
	Derive Dependent Inversion_clear	
	Derive Inversion	
	Derive Inversion_clear	
	Drop	
	 	
	e	
	End	
	Eval	
	Example	
	Existing Class	
	Existing Instance	
	Existing Instances	
	Export	
	Extract Constant	
	Extract Inductive	
	Extract Inlined Constant	
	Extraction	
	Extraction Blacklist	
	Extraction Implicit	
	Extraction Inline	
	Extraction Language	
	Extraction Library	
	Extraction NoInline	
	Extraction TestCompile	
	 	
	f	
	Fact	
	Fail	
	Fixpoint	
	Focus	
	From … Require	
	Function	
	Functional Scheme	
	 	
	g	
	Generalizable	
	Goal	
	Guarded	
	 	
	h	
	Hint Constants	
	Hint Constructors	
	Hint Cut	
	Hint Extern	
	Hint Immediate	
	Hint Mode	
	Hint Opaque	
	Hint Resolve	
	Hint Rewrite	
	Hint Transparent	
	Hint Unfold	
	Hint Variables	
	Hint View for	
	Hint View for apply	
	Hint View for move	
	Hypotheses	
	Hypothesis	
	 	
	i	
	Identity Coercion	
	Implicit Type	
	Implicit Types	
	Import	
	Include	
	Include Type	
	Inductive	
	Infix	
	Info	
	infoH	
	Inspect	
	Instance	
	 	
	l	
	Lemma	
	Let	
	Let CoFixpoint	
	Let Fixpoint	
	Load	
	Locate	
	Locate File	
	Locate Library	
	Locate Ltac	
	Locate Module	
	Locate Term	
	Ltac	
	Ltac2	
	Ltac2 Eval	
	Ltac2 external	
	Ltac2 Notation	
	Ltac2 Notation (abbreviation)	
	Ltac2 Set	
	Ltac2 Type	
	 	
	m	
	Module	
	Module Type	
	 	
	n	
	Next Obligation	
	Notation	
	Notation (abbreviation)	
	Number Notation	
	 	
	o	
	Obligation	
	Obligation Tactic	
	Obligations	
	Opaque	
	Open Scope	
	Optimize Heap	
	Optimize Proof	
	 	
	p	
	Parameter	
	Parameters	
	Prenex Implicits	
	Preterm	
	Primitive	
	Print	
	Print All	
	Print All Dependencies	
	Print Assumptions	
	Print Canonical Projections	
	Print Classes	
	Print Coercion Paths	
	Print Coercions	
	Print Custom Grammar	
	Print Debug GC	
	Print Extraction Blacklist	
	Print Extraction Inline	
	Print Firstorder Solver	
	Print Grammar	
	Print Graph	
	Print Hint	
	Print HintDb	
	Print Implicit	
	Print Instances	
	Print Libraries	
	Print LoadPath	
	Print Ltac	
	Print Ltac Signatures	
	Print ML Modules	
	Print ML Path	
	Print Module	
	Print Module Type	
	Print Opaque Dependencies	
	Print Options	
	Print Rewrite HintDb	
	Print Rings	
	Print Scope	
	Print Scopes	
	Print Section	
	Print Strategies	
	Print Strategy	
	Print Table	
	Print Tables	
	Print Transparent Dependencies	
	Print Typing Flags	
	Print Universes	
	Print Visibility	
	Proof	
	Proof `term`	
	Proof using	
	Proof with	
	Property	
	Proposition	
	Pwd	
	 	
	q	
	Qed	
	Quit	
	 	
	r	
	Record	
	Recursive Extraction	
	Recursive Extraction Library	
	Redirect	
	Register	
	Register Inline	
	Remark	
	Remove	
	Remove Hints	
	Remove LoadPath	
	Require	
	Require Export	
	Require Import	
	Reserved Infix	
	Reserved Notation	
	Reset	
	Reset Extraction Blacklist	
	Reset Extraction Inline	
	Reset Initial	
	Reset Ltac Profile	
	Restart	
	 	
	s	
	Save	
	Scheme	
	Search	
	SearchPattern	
	SearchRewrite	
	Section	
	Separate Extraction	
	Set	
	Show	
	Show Conjectures	
	Show Existentials	
	Show Goal	
	Show Intro	
	Show Intros	
	Show Lia Profile	
	Show Ltac Profile	
	Show Match	
	Show Obligation Tactic	
	Show Proof	
	Show Universes	
	Show Zify	
	Solve All Obligations	
	Solve Obligations	
	Strategy	
	String Notation	
	Structure	
	SubClass	
	Succeed	
	 	
	t	
	Tactic Notation	
	Test	
	Theorem	
	Time	
	Timeout	
	Transparent	
	Typeclasses eauto	
	Typeclasses Opaque	
	Typeclasses Transparent	
	 	
	u	
	Undelimit Scope	
	Undo	
	Unfocus	
	Unfocused	
	Universe	
	Unset	
	Unshelve	
	 	
	v	
	Variable	
	Variables	
	Variant
"""

tactics_data = """
+	
	+ (backtracking branching)	
	 	
	=	
	=>	
	 	
	[	
	[ … | … | … ] (dispatch)	
	[> … | … | … ] (dispatch)	
	 	
	a	
	abstract	
	abstract (ssreflect)	
	absurd	
	admit	
	apply	
	apply (ssreflect)	
	apply … in	
	apply … in … as	
	assert	
	assert_fails	
	assert_succeeds	
	assumption	
	auto	
	autoapply	
	autorewrite	
	autounfold	
	 	
	b	
	bfs eauto	
	btauto	
	by	
	 	
	c	
	case	
	case (ssreflect)	
	case_eq	
	casetype	
	cbn	
	cbv	
	change	
	change_no_check	
	classical_left	
	classical_right	
	clear	
	clearbody	
	cofix	
	compare	
	compute	
	congr	
	congruence	
	constr_eq	
	constr_eq_nounivs	
	constr_eq_strict	
	constructor	
	context	
	contradict	
	contradiction	
	cut	
	cutrewrite	
	cycle	
	 	
	d	
	debug auto	
	debug eauto	
	debug trivial	
	decide equality	
	decompose	
	dependent destruction	
	dependent induction	
	dependent inversion	
	dependent inversion_clear	
	dependent rewrite	
	dependent simple inversion	
	destruct	
	dintuition	
	discriminate	
	discrR	
	do	
	do (ssreflect)	
	done	
	dtauto	
	 	
	e	
	eapply	
	eassert	
	eassumption	
	easy	
	eauto	
	ecase	
	econstructor	
	edestruct	
	ediscriminate	
	eelim	
	eenough	
	eexact	
	eexists	
	einduction	
	einjection	
	eintros	
	eleft	
	elim	
	elim (ssreflect)	
	elimtype	
	enough	
	epose	
	epose proof	
	eremember	
	erewrite	
	eright	
	eset	
	esimplify_eq	
	esplit	
	etransitivity	
	eval	
	evar	
	exact	
	exact (ssreflect)	
	exact_no_check	
	exactly_once	
	exfalso	
	exists	
	 	
	f	
	f_equal	
	fail	
	field	
	field_simplify	
	field_simplify_eq	
	finish_timing	
	first	
	first (ssreflect)	
	first last	
	firstorder	
	fix	
	fold	
	fresh	
	fun	
	functional induction	
	functional inversion	
	 	
	g	
	generalize	
	generally have	
	gfail	
	give_up	
	guard	
	 	
	h	
	has_evar	
	have	
	hnf	
	 	
	i	
	idtac	
	if-then-else (Ltac2)	
	in	
	induction	
	info_auto	
	info_eauto	
	info_trivial	
	injection	
	instantiate	
	intro	
	intros	
	intros …	
	intuition	
	inversion	
	inversion_clear	
	inversion_sigma	
	is_cofix	
	is_const	
	is_constructor	
	is_evar	
	is_fix	
	is_ground	
	is_ind	
	is_proj	
	is_var	
	 	
	l	
	lapply	
	last	
	last first	
	lazy	
	lazy_match!	
	lazy_match! goal	
	lazymatch	
	lazymatch goal	
	left	
	let	
	lia	
	lra	
	ltac-seq	
	 	
	m	
	match	
	match (Ltac2)	
	match goal	
	match!	
	match! goal	
	move	
	move (ssreflect)	
	move … at bottom	
	move … at top	
	move … before …	
	multi_match!	
	multi_match! goal	
	multimatch	
	multimatch goal	
	 	
	n	
	native_cast_no_check	
	native_compute	
	nia	
	notypeclasses refine	
	now	
	now_show	
	nra	
	nsatz	
	numgoals	
	 	
	o	
	once	
	only	
	optimize_heap	
	over	
	 	
	p	
	pattern	
	pose	
	pose (ssreflect)	
	pose proof	
	progress	
	psatz	
	 	
	r	
	rapply	
	red	
	refine	
	reflexivity	
	remember	
	rename	
	repeat	
	replace	
	reset ltac profile	
	restart_timer	
	revert	
	revert dependent	
	revgoals	
	rewrite	
	rewrite (ssreflect)	
	rewrite *	
	rewrite_db	
	rewrite_strat	
	right	
	ring	
	ring_simplify	
	rtauto	
	 	
	s	
	set	
	set (ssreflect)	
	setoid_reflexivity	
	setoid_replace	
	setoid_rewrite	
	setoid_symmetry	
	setoid_transitivity	
	shelve	
	shelve_unifiable	
	show ltac profile	
	simpl	
	simple apply	
	simple congruence	
	simple destruct	
	simple eapply	
	simple induction	
	simple inversion	
	simple notypeclasses refine	
	simple refine	
	simple subst	
	simplify_eq	
	solve	
	solve_constraints	
	specialize	
	split	
	split_Rabs	
	split_Rmult	
	start ltac profiling	
	stepl	
	stepr	
	stop ltac profiling	
	subst	
	substitute	
	suff	
	suffices	
	swap	
	symmetry	
	 	
	t	
	tauto	
	time	
	time_constr	
	timeout	
	transitivity	
	transparent_abstract	
	trivial	
	try	
	tryif	
	type of	
	type_term	
	typeclasses eauto	
	 	
	u	
	under	
	unfold	
	unify	
	unlock	
	unshelve	
	 	
	v	
	vm_cast_no_check	
	vm_compute	
	 	
	w	
	with_strategy	
	without loss	
	wlog	
	 	
	z	
	zify
"""

def extract(data):
    result = map(lambda l: l.strip("\t "), data.splitlines())
    result = filter(lambda l: len(l) > 1, result)
    result = map(lambda l: l.split(" ")[0], result)
    result = filter(lambda l: l[0].isalpha(), result)
    result = map(lambda l: l.rstrip(":"), result)
    result = sorted(set(result))
    return result

print("Commands:")
for command in extract(commands_data):
    print('"{}",'.format(command))

print("Tactics:")
for tactic in extract(tactics_data):
    print('"{}",'.format(tactic))
