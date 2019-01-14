(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("codemirror/lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["codemirror/lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";

  return {
    onload: function() {

      console.info('Coq kernel script: adding CodeMirror mode.');

      // Coq mode based on source taken from: https://github.com/ejgallego/CodeMirror/blob/9a1be1c5f716301245c27d4c541358835c1694fe/mode/coq/coq.js
      // Vernacular and tactics updated for 8.8.2
      // Also see: https://github.com/EugeneLoy/coq_jupyter/issues/19

      CodeMirror.defineMode('coq', function(_config, _parserConfig) {

        var vernacular = [
          "Abort",
          "About",
          "Add",
          "Admit",
          "Admitted",
          "Arguments",
          "Axiom",
          "Axioms",
          "Back",
          "BackTo",
          "Backtrack",
          "Bind",
          "Canonical",
          "Cd",
          "Check",
          "Class",
          "Close",
          "CoFixpoint",
          "CoInductive",
          "Coercion",
          "Collection",
          "Combined",
          "Compute",
          "Conjecture",
          "Conjectures",
          "Constraint",
          "Context",
          "Corollary",
          "Create",
          "Cumulative",
          "Declare",
          "Defined",
          "Definition",
          "Delimit",
          "Derive",
          "Drop",
          "End",
          "Eval",
          "Example",
          "Existential",
          "Existing",
          "Export",
          "Extract",
          "Extraction",
          "Fact",
          "Fail",
          "Fixpoint",
          "Focus",
          "Function",
          "Functional",
          "Generalizable",
          "Global",
          "Goal",
          "Grab",
          "Guarded",
          "Hint",
          "Hypotheses",
          "Hypothesis",
          "Identity",
          "Implicit",
          "Import",
          "Include",
          "Inductive",
          "Infix",
          "Info",
          "Inline",
          "Inspect",
          "Instance",
          "Lemma",
          "Let",
          "Load",
          "Local",
          "Locate",
          "Ltac",
          "Module",
          "Monomorphic",
          "Next",
          "NonCumulative",
          "Notation",
          "Obligation",
          "Obligations",
          "Opaque",
          "Open",
          "Optimize",
          "Parameter",
          "Parameters",
          "Polymorphic",
          "Prenex",
          "Preterm",
          "Print",
          "Program",
          "Proof",
          "Proposition",
          "Pwd",
          "Qed",
          "Quit",
          "Record",
          "Recursive",
          "Redirect",
          "Remark",
          "Remove",
          "Require",
          "Reset",
          "Restart",
          "Save",
          "Scheme",
          "Search",
          "SearchAbout",
          "SearchHead",
          "SearchPattern",
          "SearchRewrite",
          "Section",
          "Separate",
          "Set",
          "Show",
          "Solve",
          "Strategy",
          "Structure",
          "Tactic",
          "Test",
          "Theorem",
          "Time",
          "Timeout",
          "Transparent",
          "Typeclasses",
          "Undelimit",
          "Undo",
          "Unfocus",
          "Unfocused",
          "Universe",
          "Unset",
          "Unshelve",
          "Variable",
          "Variables",
          "Variant"
        ];

        var gallina = [
          'as',
          'at',
          'cofix', 'crush',
          'else', 'end',
          'False', 'fix', 'for', 'forall', 'fun',
          'if', 'in', 'is',
          'let',
          'match',
          'of',
          'Prop',
          'return',
          'struct',
          'then', 'True', 'Type',
          'when', 'with'
        ];

        var tactics = [
          "abstract",
          "absurd",
          "admit",
          "all",
          "apply",
          "assert",
          "assert_fails",
          "assert_succeeds",
          "assumption",
          "auto",
          "autoapply",
          "autorewrite",
          "autounfold",
          "btauto",
          "by",
          "case",
          "cbn",
          "cbv",
          "change",
          "classical_left",
          "classical_right",
          "clear",
          "clearbody",
          "cofix",
          "compare",
          "compute",
          "congr",
          "congruence",
          "constr_eq",
          "constructor",
          "contradict",
          "contradiction",
          "cut",
          "cutrewrite",
          "cycle",
          "debug",
          "decide",
          "decompose",
          "dependent",
          "destruct",
          "dintuition",
          "discrR",
          "discriminate",
          "do",
          "done",
          "double",
          "dtauto",
          "eapply",
          "eassert",
          "eassumption",
          "easy",
          "eauto",
          "ecase",
          "econstructor",
          "edestruct",
          "ediscriminate",
          "eelim",
          "eenough",
          "eexact",
          "eexists",
          "einduction",
          "einjection",
          "eleft",
          "elim",
          "elimtype",
          "enough",
          "epose",
          "eremember",
          "erewrite",
          "eright",
          "eset",
          "esimplify_eq",
          "esplit",
          "evar",
          "exact",
          "exactly_once",
          "exfalso",
          "exists",
          "f_equal",
          "fail",
          "field",
          "field_simplify",
          "field_simplify_eq",
          "finish_timing",
          "first",
          "firstorder",
          "fix",
          "fold",
          "fourier",
          "function",
          "functional",
          "generalize",
          "generally",
          "gfail",
          "give_up",
          "guard",
          "has_evar",
          "have",
          "hnf",
          "idtac",
          "in",
          "induction",
          "info_trivial",
          "injection",
          "instantiate",
          "intro",
          "intros",
          "intuition",
          "inversion",
          "is_evar",
          "is_var",
          "lapply",
          "last",
          "lazy",
          "left",
          "let",
          "lia",
          "lra",
          "ltac-seq",
          "match",
          "move",
          "native_compute",
          "nia",
          "notypeclasses",
          "now",
          "nra",
          "nsatz",
          "omega",
          "once",
          "only",
          "optimize_heap",
          "par",
          "pattern",
          "pose",
          "progress",
          "psatz",
          "quote",
          "red",
          "refine",
          "reflexivity",
          "remember",
          "rename",
          "repeat",
          "replace",
          "reset",
          "restart_timer",
          "revert",
          "revgoals",
          "rewrite",
          "rewrite_strat",
          "right",
          "ring",
          "ring_simplify",
          "romega",
          "rtauto",
          "set",
          "setoid_reflexivity",
          "setoid_replace",
          "setoid_rewrite",
          "setoid_symmetry",
          "setoid_transitivity",
          "shelve",
          "shelve_unifiable",
          "show",
          "simpl",
          "simple",
          "simplify_eq",
          "solve",
          "specialize",
          "split",
          "split_Rabs",
          "split_Rmult",
          "start",
          "stepl",
          "stepr",
          "stop",
          "subst",
          "suff",
          "suffices",
          "swap",
          "symmetry",
          "tauto",
          "time",
          "time_constr",
          "timeout",
          "transitivity",
          "transparent_abstract",
          "trivial",
          "try",
          "tryif",
          "typeclasses",
          "unfold",
          "unify",
          "unlock",
          "vm_compute",
          "without",
          "wlog"
        ];

        var terminators = [
          'assumption',
          'by',
          'contradiction',
          'discriminate',
          'exact',
          'now',
          'omega',
          'reflexivity',
          'tauto'
        ];

        var admitters = [
          'admit',
          'Admitted'
        ];

        // Map assigning each keyword a category.
        var words = {};

        // TODO the following mappings are temporary modified.
        // TODO should change these again as part of https://github.com/EugeneLoy/coq_jupyter/issues/19
        // We map
        // - gallina keywords -> CM keywords
        // - vernaculars      -> CM builtins
        // - admitters        -> CM keywords XXX
        gallina    .map(function(word){words[word] = 'builtin';});
        admitters  .map(function(word){words[word] = 'builtin';});
        vernacular .map(function(word){words[word] = 'keyword';});

        tactics    .map(function(word){words[word] = 'builtin';});
        terminators.map(function(word){words[word] = 'builtin';});

        /*
          Coq mode defines the following state variables:

          - begin_sentence: only \s caracters seen from the last sentence.

          - commentLevel [:int] = Level of nested comments.

          - tokenize [:func] = current active tokenizer. We provide 4 main ones:

            + tokenBase: Main parser, it reads the next character and
              setups the next tokenizer. In particular it takes care of
              braces. It doesn't properly analyze the sentences and
              bracketing.

            + tokenStatementEnd: Called when a dot is found in tokenBase,
              it looks ahead on the string and returns statement end.

            + tokenString: Takes care of escaping.

            + tokenComment: Takes care of nested comments.

         */

        /*
          Codemirror lexing functions:

          - eat(s) = eat next char if s
          - eatWhile(s) = eat s until fails
          - match(regexp) => return array of matches and optionally eat

         */
        function tokenBase(stream, state) {

          // If any space in the input, return null.
          if(stream.eatSpace())
            return null;

          var ch = stream.next();

          if(state.begin_sentence && (/[-*+{}]/.test(ch)))
            return 'coq-bullet';

          // Preserve begin sentence after comment.
          if (ch === '(') {
            if (stream.peek() === '*') {
              stream.next();
              state.commentLevel++;
              state.tokenize = tokenComment;
              return state.tokenize(stream, state);
            }
            state.begin_sentence = false;
            return 'parenthesis';
          }

          if( ! (/\s/.test(ch)) ) {
            state.begin_sentence = false;
          }

          if(ch === '.') {
            // Parse .. specially.
            if(stream.peek() !== '.') {
              state.tokenize = tokenStatementEnd;
              return state.tokenize(stream, state);
            } else {
              stream.next();
              return 'operator';
            }

          }

          if (ch === '"') {
            state.tokenize = tokenString;
            return state.tokenize(stream, state);
          }

          if(ch === ')')
            return 'parenthesis';

          if (ch === '~') {
            stream.eatWhile(/\w/);
            return 'variable-2';
          }

          if (ch === '`') {
            stream.eatWhile(/\w/);
            return 'quote';
          }

          if (/\d/.test(ch)) {
            stream.eatWhile(/[\d]/);
            /*
            if (stream.eat('.')) {
              stream.eatWhile(/[\d]/);
            }
            */
            return 'number';
          }

          if ( /[+\-*&%=<>!?|]/.test(ch)) {
            return 'operator';
          }

          if(/[\[\]]/.test(ch)) {
            return 'bracket';
          }

          stream.eatWhile(/\w/);
          var cur = stream.current();
          return words.hasOwnProperty(cur) ? words[cur] : 'variable';

        }

        function tokenString(stream, state) {
          var next, end = false, escaped = false;
          while ((next = stream.next()) != null) {
            if (next === '"' && !escaped) {
              end = true;
              break;
            }
            escaped = !escaped && next === '\\';
          }
          if (end && !escaped) {
            state.tokenize = tokenBase;
          }
          return 'string';
        }

        function tokenComment(stream, state) {
          var ch;
          while(state.commentLevel && (ch = stream.next())) {
            if(ch === '(' && stream.peek() === '*') {
              stream.next();
              state.commentLevel++;
            }

            if(ch === '*' && stream.peek() === ')') {
              stream.next();
              state.commentLevel--;
            }
          }

          if(!state.commentLevel)
            state.tokenize = tokenBase;

          return 'comment';
        }

        function tokenStatementEnd(stream, state) {
          state.tokenize = tokenBase;

          if(stream.eol() || stream.match(/\s/, false)) {
            state.begin_sentence = true;
            return 'statementend';
          }
        }

        return {
          startState: function() {
            return {begin_sentence: true, tokenize: tokenBase, commentLevel: 0};
          },

          token: function(stream, state) {
            return state.tokenize(stream, state);
          },

          blockCommentStart: "(*",
          blockCommentEnd  : "*)",
          lineComment: null
        };
      });

      CodeMirror.defineMIME('text/x-coq', {
        name: 'coq'
      });

      console.info('Coq kernel script: adding actions/shortcuts.');

      var action = {
        icon: 'fa-step-backward',
        cmd: 'Rollback cell',
        help: 'Rollback cell',
        help_index: 'zz', // TODO not shure what to set here
        handler: function () {
          $(".cell.selected .enabled_rollback_button, .cell.jupyter-soft-selected .enabled_rollback_button").triggerHandler("click");
        }
      };
      var prefix = 'coq_jupyter';
      var action_name = 'rollback-cell';

      var jupyter = require('base/js/namespace');
      var full_action_name = jupyter.actions.register(action, action_name, prefix);
      jupyter.toolbar.add_buttons_group([full_action_name]);
      jupyter.keyboard_manager.command_shortcuts.add_shortcut('Ctrl-Backspace', full_action_name);

      console.info('Coq kernel script loaded.');
    }
  };

});
