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

    version: '1.4.0',

    onload: function() {
      console.info('Loading Coq kernel script, version: ' + this.version);

      var self = this;
      var jupyter = require('base/js/namespace');

      // TODO find better way to expose coq kernel
      window.CoqKernel = this;

      this.init_CodeMirror();
      this.patch();
      this.init_shortcuts();
      this.init_kernel_comm();

      jupyter.notebook.kernel.events.on('kernel_ready.Kernel', function (evt, info) {
        self.init_kernel_comm();
      });

      console.info('Coq kernel script loaded.');
    },

    init_CodeMirror: function() {
      console.info('Coq kernel script: adding CodeMirror mode.');

      // Coq mode based on source taken from: https://github.com/ejgallego/CodeMirror/blob/9a1be1c5f716301245c27d4c541358835c1694fe/mode/coq/coq.js
      // Vernacular and tactics updated for 8.9.0
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
          "Numeral",
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
          "SubClass",
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
          "constr_eq_strict",
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
          "inversion_sigma",
          "is_evar",
          "is_var",
          "lapply",
          "last",
          "lazy",
          "left",
          "let",
          "lia",
          "lra",
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
    },

    patch: function() {
      console.info('Coq kernel script: patching CodeCell.execute.');

      // based on: https://gist.github.com/quinot/e3801b09f754efb0f39ccfbf0b50eb40

      var self = this;
      var codecell = require('notebook/js/codecell');

      var original_execute = codecell.CodeCell.prototype.execute;
      codecell.CodeCell.prototype.execute = function(stop_on_error) {
          var cell = this;

          if (!this.coq_kernel_kernel_patched) {
            this.coq_kernel_kernel_patched = true;

            this.coq_kernel_original_kernel = this.kernel;
            this.kernel = new Proxy(
              this.coq_kernel_original_kernel,
              {
                "get": function(target, prop, receiver) {
                  if (prop == "execute") {
                    return function(code, callbacks, metadata) {
                        return self.execute_cell(cell, code, callbacks, metadata);
                    };
                  } else {
                    return target[prop];
                  }
                }
              }
            );
          }

          original_execute.call(this, stop_on_error)
      };

      console.info('Coq kernel script: patching OutputArea.append_execute_result.');

      var outputarea = require('notebook/js/outputarea');
      var original_append_execute_result = outputarea.OutputArea.prototype.append_execute_result;
      outputarea.OutputArea.prototype.append_execute_result = function(json) {
        var result = original_append_execute_result.call(this, json);
        // Enable rollback button. This is done here since rollback button relies
        // on successfull operation of kernel.js script. In case frontend does not
        // support kernel.js the button will remain hidden to end user providing
        // ad-hoc fallback.
        $(this.element[0]).find(".coq_kernel_roll_back_button_area").toggle(true);
        return result;
      };
    },

    init_shortcuts: function() {
      console.info('Coq kernel script: adding actions/shortcuts.');

      var self = this;
      var jupyter = require('base/js/namespace');

      var action = {
        icon: 'fa-step-backward',
        cmd: 'Rollback cell',
        help: 'Rollback cell',
        help_index: 'zz', // TODO not sure what to set here
        handler: function () {
          var jupyter = require('base/js/namespace');
          var cells = jupyter.notebook.get_cells();
          for (var i = 0; i < cells.length; i++) {
            if (cells[i].selected || cells[i].element.hasClass('jupyter-soft-selected')) {
              self.roll_back_cell(cells[i]);
            }
          }
        }
      };
      var prefix = 'coq_jupyter';
      var action_name = 'rollback-cell';

      var full_action_name = jupyter.actions.register(action, action_name, prefix);
      jupyter.toolbar.add_buttons_group([full_action_name]);
      jupyter.keyboard_manager.command_shortcuts.add_shortcut('Ctrl-Backspace', full_action_name);
    },

    init_kernel_comm: function() {
      console.info('Coq kernel script: opening kernel comm.');

      var self = this;
      var jupyter = require('base/js/namespace');

      this.kernel_comm = jupyter.notebook.kernel.comm_manager.new_comm('coq_kernel.kernel_comm', {});
      this.kernel_comm.on_msg(function(message) {
        self.handle_kernel_comm_message(message);
      });

      // TODO handle kernel restart
    },

    handle_kernel_comm_message: function(message) {
      if (message.content.data.comm_msg_type === "kernel_comm_opened") {
        console.info('Kernel comm opened. comm_id: ' + message.content.comm_id);
        var history = message.content.data.history
        for (var i = 0; i < history.length; i++) {
          this.update_cell_output(
            history[i].execution_id,
            history[i].evaluated,
            history[i].rolled_back
          );
        }
      } else if (message.content.data.comm_msg_type === "cell_state") {
        console.info('Cell state updated. execution_id: ' + message.content.data.execution_id);
        this.update_cell_output(
          message.content.data.execution_id,
          message.content.data.evaluated,
          message.content.data.rolled_back
        );
      } else {
        console.error('Unexpected comm message: ' + JSON.stringify(message));
      }
    },

    execute_cell: function(cell, code, callbacks, metadata) {
      // reuse "execute_request" message id as "execution_id" used by coq kernel
      // to track cell executions
      cell.metadata.execution_id = cell.coq_kernel_original_kernel.execute(code, callbacks, metadata);

      return cell.metadata.execution_id;
    },

    roll_back_cell: function(cell) {
      if (cell.metadata.execution_id != undefined) {
        $(cell.element[0]).find(".coq_kernel_roll_back_button").prop('disabled', true);

        this.kernel_comm.send({
          'comm_msg_type': 'roll_back',
          "execution_id": cell.metadata.execution_id
        });
      }
    },

    roll_back: function(button) {
      this.roll_back_cell(this.get_cell_by_element(button));
    },

    get_cell_by_element: function(element) {
      var jupyter = require('base/js/namespace');
      var cells = jupyter.notebook.get_cells();
      for (var i = 0; i < cells.length; i++) {
        if ($.contains(cells[i].element[0], element)) {
          return cells[i];
        }
      }
    },

    update_cell_output: function(execution_id, evaluated, rolled_back) {
      $(".coq_kernel_output_area_" + execution_id).toggle(!rolled_back);
      $(".coq_kernel_roll_back_message_" + execution_id).toggle(rolled_back);
      $(".coq_kernel_roll_back_button_area_" + execution_id).toggle(evaluated && !rolled_back);
    }

  };

});
