
// Coq mode created by Valentin Robert, Benoît Pin, Emilio J. Gallego
// Arias, and others

// Coq mode source taken from: https://github.com/ejgallego/CodeMirror/blob/coq-mode/mode/coq/coq.js

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("codemirror/lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["codemirror/lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";

  CodeMirror.defineMode('coq', function(_config, _parserConfig) {

    var vernacular = [
      'Abort', 'About', 'Add', 'All', 'Arguments', 'Asymmetric', 'Axiom',
      'Bind',
      'Canonical', 'Check', 'Class', 'Close', 'Coercion', 'CoFixpoint', 'Comments',
      'CoInductive', 'Context', 'Constructors', 'Contextual', 'Corollary',
      'Defined', 'Definition', 'Delimit',
      'Fail',
      'Eval',
      'End', 'Example', 'Export',
      'Fact', 'Fixpoint', 'From',
      'Global', 'Goal', 'Graph',
      'Hint', 'Hypotheses', 'Hypothesis',
      'Implicit', 'Implicits', 'Import', 'Inductive', 'Infix', 'Instance',
      'Lemma', 'Let', 'Local', 'Ltac',
      'Module', 'Morphism',
      'Next', 'Notation',
      'Obligation', 'Open',
      'Parameter', 'Parameters', 'Prenex', 'Print', 'Printing', 'Program',
      'Patterns', 'Projections', 'Proof',
      'Proposition',
      'Qed',
      'Record', 'Relation', 'Remark', 'Require', 'Reserved', 'Resolve', 'Rewrite',
      'Save', 'Scope', 'Search', 'SearchAbout', 'Section', 'Set', 'Show', 'Strict', 'Structure',
      'Tactic', 'Time', 'Theorem', 'Types',
      'Unset',
      'Variable', 'Variables', 'View'
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
      'after', 'apply', 'assert', 'auto', 'autorewrite',
      'case', 'change', 'clear', 'compute', 'congruence', 'constructor',
      'congr', 'cut', 'cutrewrite',
      'dependent', 'destruct',
      'eapply', 'eassumption', 'eauto', 'econstructor', 'elim', 'exists',
      'field', 'firstorder', 'fold', 'fourier',
      'generalize',
      'have', 'hnf',
      'induction', 'injection', 'instantiate', 'intro', 'intros', 'inversion',
      'left',
      'move',
      'pattern', 'pose',
      'refine', 'remember', 'rename', 'replace', 'revert', 'rewrite',
      'right', 'ring',
      'set', 'simpl', 'specialize', 'split', 'subst', 'suff', 'symmetry',
      'transitivity', 'trivial',
      'unfold', 'unlock', 'using',
      'vm_compute',
      'where', 'wlog'
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

    // We map
    // - gallina keywords -> CM keywords
    // - vernaculars      -> CM builtins
    // - admitters        -> CM keywords XXX
    gallina    .map(function(word){words[word] = 'keyword';});
    admitters  .map(function(word){words[word] = 'keyword';});
    vernacular .map(function(word){words[word] = 'builtin';});

    tactics    .map(function(word){words[word] = 'tactic';});
    terminators.map(function(word){words[word] = 'terminator';});

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

  return {
    onload: function() {
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
