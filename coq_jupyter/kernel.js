define([
  'base/js/namespace',
  'notebook/js/codecell',
  'notebook/js/outputarea',
  'codemirror/lib/codemirror'
], function (
  Jupyter,
  CodeCell,
  OutputArea,
  CodeMirror
) {
  "use strict";

  var self = {

    version: '1.5.1',

    onload: function() {
      console.info('Loading Coq kernel script, version: ' + self.version);

      // TODO find better way to expose coq kernel
      window.CoqKernel = self;

      self.init_CodeMirror();
      self.patch();
      self.init_shortcuts();
      self.init_kernel_comm();

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

      var original_execute = CodeCell.CodeCell.prototype.execute;
      CodeCell.CodeCell.prototype.execute = function(stop_on_error) {
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

      console.info('Coq kernel script: patching CodeCell.create_element.');
      var original_create_element = CodeCell.CodeCell.prototype.create_element;
      CodeCell.CodeCell.prototype.create_element = function() {
        var cell = this;
        setTimeout(function() { self.on_create_element(cell); }, 0);
        return original_create_element.call(this);
      };

      console.info('Coq kernel script: patching OutputArea.append_execute_result.');

      var original_append_execute_result = OutputArea.OutputArea.prototype.append_execute_result;
      OutputArea.OutputArea.prototype.append_execute_result = function(json) {
        var result = original_append_execute_result.call(this, json);
        self.on_append_execute_result(this, json);
        return result;
      };
    },

    init_shortcuts: function() {
      console.info('Coq kernel script: adding actions/shortcuts.');

      var action = {
        icon: 'fa-step-backward',
        cmd: 'Rollback cell',
        help: 'Rollback cell',
        help_index: 'zz', // TODO not sure what to set here
        handler: function () {
          var cells = Jupyter.notebook.get_cells();
          for (var c = 0; c < cells.length; c++) {
            if (cells[c].selected || cells[c].element.hasClass('jupyter-soft-selected')) {
              self.roll_back_cell(cells[c]);
            }
          }
        }
      };
      var prefix = 'coq_jupyter';
      var action_name = 'rollback-cell';

      var full_action_name = Jupyter.actions.register(action, action_name, prefix);
      Jupyter.toolbar.add_buttons_group([full_action_name]);
      Jupyter.keyboard_manager.command_shortcuts.add_shortcut('Ctrl-Backspace', full_action_name);
    },

    init_kernel_comm: function() {
      if (Jupyter.notebook.kernel) {
        console.info('Coq kernel script: initializing kernel comm.');
        Jupyter.notebook.kernel.events.on('kernel_ready.Kernel', function (evt, info) {
          self.open_kernel_comm();
        });
        self.open_kernel_comm();
      } else {
        console.info('Coq kernel script: kernel is not ready - postponing kernel comm initialization.');
        setTimeout(self.init_kernel_comm,  100);
      }
    },

    open_kernel_comm: function() {
      console.info('Coq kernel script: opening kernel comm.');
      if (self.kernel_comm !== undefined) {
        self.close_kernel_comm();
      }
      self.kernel_comm = Jupyter.notebook.kernel.comm_manager.new_comm('coq_kernel.kernel_comm');
      self.kernel_comm.on_msg(function(message) {
        self.handle_kernel_comm_message(message);
      });
      console.info('Coq kernel script: kernel comm opened.');
    },

    close_kernel_comm: function() {
      console.info('Coq kernel script: closing kernel comm : ' + self.kernel_comm.comm_id);
      try {
        self.kernel_comm.close();
        Jupyter.notebook.kernel.comm_manager.unregister_comm(self.kernel_comm);
      } catch(e) {
        console.error(e);
      }
    },

    handle_kernel_comm_message: function(message) {
      if (message.content.data.comm_msg_type === "kernel_comm_opened") {
        console.info('Kernel comm opened. comm_id: ' + message.content.comm_id);
        self.on_history_received(message.content.data.history);
      } else if (message.content.data.comm_msg_type === "cell_state") {
        console.info('Cell state updated. execution_id: ' + message.content.data.execution_id);
        self.on_cell_state_received(message.content.data.execution_id, message.content.data.evaluated, message.content.data.rolled_back);
      } else {
        console.error('Unexpected comm message: ' + JSON.stringify(message));
      }
    },

    execute_cell: function(cell, code, callbacks, metadata) {
      var previous_execution_id = self.get_metadata(cell, "execution_id");

      self.reset_metadata(cell);

      if (self.get_metadata(cell, "auto_roll_back") && previous_execution_id !== undefined) {
        metadata.coq_kernel_roll_back_cell = previous_execution_id;
      }

      // reuse kernel message id as execution id for this cell
      var execution_id = cell.coq_kernel_original_kernel.execute(code, callbacks, metadata);

      self.bind_execution_id(cell, execution_id)

      return execution_id;
    },

    on_append_execute_result: function(outputarea, json) {
      var cell = self.get_cell_by_element(outputarea.element[0])
      self.set_metadata(cell, "evaluated", json.metadata.coq_kernel_evaluated);
      self.set_metadata(cell, "rolled_back", json.metadata.coq_kernel_rolled_back);
      self.update_rich_cell_output(cell);
    },

    on_create_element: function(cell) {
      if (!self.has_valid_metadata(cell)) {
        self.reset_metadata(cell);
      }
      self.update_rich_cell_output(cell);
    },

    on_cell_state_received: function(execution_id, evaluated, rolled_back) {
      var cells = Jupyter.notebook.get_cells();
      for (var c = 0; c < cells.length; c++) {
        if (self.has_valid_metadata(cells[c]) && self.get_metadata(cells[c], "execution_id") === execution_id) {
          self.update_cell_state_metadata(cells[c], evaluated, rolled_back);
          self.update_rich_cell_output(cells[c]);
          break;
        }
      }
    },

    on_history_received: function(history) {
      var cells = Jupyter.notebook.get_cells();
      for (var c = 0; c < cells.length; c++) {
        var execution_id = self.get_metadata(cells[c], "execution_id");

        self.reset_metadata(cells[c]);
        if (execution_id !== undefined) {
          // rebind execution ids to cells. This is typically needed after loading
          // since cell ids are not persisted.
          self.bind_execution_id(cells[c], execution_id);
        }

        for (var h = 0; h < history.length; h++) {
          if (self.get_metadata(cells[c], "execution_id") === history[h].execution_id) {
            self.update_cell_state_metadata(cells[c], history[h].evaluated, history[h].rolled_back);
            break;
          }
        }

        self.update_rich_cell_output(cells[c]);
      }
    },

    reset_metadata: function(cell) {
      if (cell.metadata.coq_kernel_metadata === undefined) {
        cell.metadata.coq_kernel_metadata = {
          "auto_roll_back": true
        };
      }

      cell.metadata.coq_kernel_metadata.execution_id = undefined;
      cell.metadata.coq_kernel_metadata.cell_id = undefined;
      cell.metadata.coq_kernel_metadata.evaluated = undefined;
      cell.metadata.coq_kernel_metadata.rolled_back = undefined;
    },

    has_valid_metadata: function(cell) {
      return (
        cell.metadata.coq_kernel_metadata !== undefined &&
        cell.metadata.coq_kernel_metadata.cell_id === cell.cell_id &&
        cell.metadata.coq_kernel_metadata.execution_id !== undefined &&
        cell.metadata.coq_kernel_metadata.evaluated !== undefined &&
        cell.metadata.coq_kernel_metadata.rolled_back !== undefined &&
        cell.metadata.coq_kernel_metadata.auto_roll_back !== undefined
      );
    },

    get_metadata: function(cell, name) {
      if (cell.metadata.coq_kernel_metadata === undefined) {
        self.reset_metadata(cell);
      }
      return cell.metadata.coq_kernel_metadata[name];
    },

    set_metadata: function(cell, name, value) {
      if (cell.metadata.coq_kernel_metadata === undefined) {
        self.reset_metadata(cell);
      }
      cell.metadata.coq_kernel_metadata[name] = value;
    },

    bind_execution_id: function(cell, execution_id) {
      self.set_metadata(cell, "execution_id", execution_id);
      self.set_metadata(cell, "cell_id", cell.cell_id);
    },

    update_cell_state_metadata: function(cell, evaluated, rolled_back) {
      self.set_metadata(cell, "evaluated", evaluated);
      self.set_metadata(cell, "rolled_back", rolled_back);
    },

    roll_back_cell: function(cell) {
      $(cell.element[0]).find(".coq_kernel_roll_back_button").prop('disabled', true);

      self.kernel_comm.send({
        'comm_msg_type': 'roll_back',
        "execution_id": self.get_metadata(cell, "execution_id")
      });
    },

    roll_back: function(button) {
      self.roll_back_cell(self.get_cell_by_element(button));
    },

    toggle_auto_roll_back: function(input) {
      self.set_metadata(self.get_cell_by_element(input), "auto_roll_back", input.checked);
    },

    get_cell_by_element: function(element) {
      var cells = Jupyter.notebook.get_cells();
      for (var c = 0; c < cells.length; c++) {
        if ($.contains(cells[c].element[0], element)) {
          return cells[c];
        }
      }
    },

    update_rich_cell_output: function(cell) {
      self.hide_rich_cell_output(cell);

      if (self.has_valid_metadata(cell)) {
        var evaluated = self.get_metadata(cell, "evaluated");
        var rolled_back = self.get_metadata(cell, "rolled_back");
        var auto_roll_back = self.get_metadata(cell, "auto_roll_back");

        $(cell.element[0]).find(".coq_kernel_output_area").toggle(!rolled_back);

        $(cell.element[0]).find(".coq_kernel_status_message_area").toggle(!rolled_back)
        $(cell.element[0]).find(".coq_kernel_rolled_back_status_message").toggle(rolled_back);

        $(cell.element[0]).find(".coq_kernel_roll_back_controls_area").toggle(evaluated && !rolled_back);

        $(cell.element[0]).find(".coq_kernel_auto_roll_back_checkbox").prop('checked', auto_roll_back);
      }
    },

    hide_rich_cell_output: function(cell) {
      $(cell.element[0]).find(".coq_kernel_rich_cell_output").toggle(false);
    }

  };

  return self;

});
