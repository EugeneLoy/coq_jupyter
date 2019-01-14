
# TODO find a better way to do this
# This script parses coq tactics\commands index pages and outputs relevant
# keywords to be used in CodeMirror coq mode
# X_data variables are taken from Coq 8.8.2 documentation

commands_data = """
	a
	Abort
	About
	Add @table
	Add Field
	Add LoadPath
	Add ML Path
	Add Morphism
	Add Parametric Morphism
	Add Parametric Relation
	Add Rec LoadPath
	Add Rec ML Path
	Add Relation
	Add Ring
	Add Setoid
	Admit Obligations
	Admitted
	Arguments
	Arguments (implicits)
	Arguments (scopes)
	Axiom
	Axioms

	b
	Back
	BackTo
	Backtrack
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
	Compute
	Conjecture
	Conjectures
	Constraint
	Context
	Corollary
	Create HintDb
	Cumulative

	d
	Declare Implicit Tactic
	Declare Instance
	Declare Left Step
	Declare ML Module
	Declare Module
	Declare Reduction
	Declare Right Step
	Defined
	Definition
	Delimit Scope
	Derive
	Derive Inversion
	Drop

	e
	End
	Eval
	Example
	Existential
	Existing Class
	Existing Instance
	Export
	Extract Constant
	Extract Inductive
	Extract Inlined Constant
	Extraction
	Extraction Blacklist
	Extraction Implicit
	Extraction Inline
	Extraction Language Haskell
	Extraction Language OCaml
	Extraction Language Scheme
	Extraction Library
	Extraction NoInline
	Extraction TestCompile

	f
	Fact
	Fail
	Fixpoint
	Focus
	Function
	Functional Scheme

	g
	Generalizable
	Generalizable All Variables
	Generalizable No Variables
	Global
	Global Close Scope
	Global Generalizable
	Global Opaque
	Global Open Scope
	Global Transparent
	Goal
	Grab Existential Variables
	Guarded

	h
	Hint
	Hint ( Transparent | Opaque )
	Hint Constructors
	Hint Extern
	Hint Immediate
	Hint Resolve
	Hint Rewrite
	Hint Unfold
	Hint View for
	Hint View for apply
	Hint View for move
	Hypotheses
	Hypothesis

	i
	Identity Coercion
	Implicit Types
	Import
	Include
	Inductive
	Infix
	Info
	Inline
	Inspect
	Instance

	l
	Lemma
	Let
	Let CoFixpoint
	Let Fixpoint
	Load
	Local
	Local Close Scope
	Local Definition
	Local Notation
	Local Open Scope
	Local Parameter
	Locate
	Locate File
	Locate Library
	Ltac

	m
	Module
	Module Type
	Monomorphic

	n
	Next Obligation
	NonCumulative
	Notation

	o
	Obligation num
	Obligation Tactic
	Obligations
	Opaque
	Open Scope
	Optimize Heap
	Optimize Proof

	p
	Parameter
	Parameters
	Polymorphic
	Prenex Implicits
	Preterm
	Print
	Print All
	Print All Dependencies
	Print Assumptions
	Print Canonical Projections
	Print Classes
	Print Coercion Paths
	Print Coercions
	Print Extraction Blacklist
	Print Extraction Inline
	Print Firstorder Solver
	Print Grammar constr
	Print Grammar pattern
	Print Grammar tactic
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
	Print Scope
	Print Scopes
	Print Strategy
	Print Table @table
	Print Tables
	Print Term
	Print Transparent Dependencies
	Print Universes
	Print Visibility
	Program Definition
	Program Fixpoint
	Program Instance
	Program Lemma
	Proof
	Proof `term`
	Proof using
	Proof with
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
	Remark
	Remove @table
	Remove Hints
	Remove LoadPath
	Require
	Require Export
	Require Import
	Reset
	Reset Extraction Blacklist
	Reset Extraction Inline
	Reset Ltac Profile
	Restart

	s
	Save
	Scheme
	Scheme Equality
	Search
	Search (ssreflect)
	SearchAbout
	SearchHead
	SearchPattern
	SearchRewrite
	Section
	Separate Extraction
	Set
	Set @option
	Show
	Show Conjectures
	Show Existentials
	Show Intro
	Show Intros
	Show Ltac Profile
	Show Obligation Tactic
	Show Proof
	Show Script
	Show Universes
	Solve All Obligations
	Solve Obligations
	Strategy
	Structure

	t
	Tactic Notation
	Test
	Test @table for
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
	Unset @option
	Unshelve

	v
	Variable
	Variables
	Variant
"""

tactics_data = """
	+
	+ (backtracking branching)

	.
	... : ... (goal selector)
	... : ... (ssreflect)

	=
	=>

	[
	[> ... | ... | ... ] (dispatch)

	_
	_

	a
	abstract
	abstract (ssreflect)
	absurd
	admit
	all: ...
	apply
	apply (ssreflect)
	apply ... in
	apply ... in ... as
	assert
	assert_fails
	assert_succeeds
	assumption
	auto
	autoapply
	autorewrite
	autounfold

	b
	btauto
	by

	c
	case
	case (ssreflect)
	cbn
	cbv
	change
	classical_left
	classical_right
	clear
	clearbody
	cofix
	compare
	compute
	congr
	congruence
	congruence with
	constr_eq
	constructor
	contradict
	contradiction
	cut
	cutrewrite
	cycle

	d
	debug auto
	debug trivial
	decide equality
	decompose
	dependent destruction
	dependent induction
	dependent inversion
	dependent inversion ... with ...
	dependent rewrite ->
	dependent rewrite <-
	destruct
	destruct ... eqn:
	dintuition
	discriminate
	discrR
	do
	do (ssreflect)
	done
	double induction
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
	eleft
	elim
	elim (ssreflect)
	elim ... with
	elimtype
	enough
	epose
	eremember
	erewrite
	eright
	eset
	esimplify_eq
	esplit
	evar
	exact
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
	fourier
	function induction
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
	in
	induction
	induction ... using ...
	info_trivial
	injection
	instantiate
	intro
	intros
	intros ...
	intuition
	inversion
	is_evar
	is_var

	l
	lapply
	last
	last first
	lazy
	left
	let ... := ...
	lia
	lra
	ltac-seq

	m
	match goal
	move
	move ... after ...
	move ... at bottom
	move ... at top
	move ... before ...

	n
	native_compute
	nia
	notypeclasses refine
	now
	nra
	nsatz

	o
	omega
	once
	only ... : ...
	optimize_heap

	p
	par: ...
	pattern
	pose
	pose (ssreflect)
	pose proof
	progress
	psatz

	q
	quote

	r
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
	rewrite_strat
	right
	ring
	ring_simplify
	romega
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
	simple destruct
	simple eapply
	simple induction
	simple inversion
	simple notypeclasses refine
	simple refine
	simplify_eq
	solve
	specialize
	split
	split_Rabs
	split_Rmult
	start ltac profiling
	stepl
	stepr
	stop ltac profiling
	subst
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
	typeclasses eauto

	u
	unfold
	unify
	unlock

	v
	vm_compute

	w
	without loss
	wlog

	|
	|| (left-biased branching)
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
