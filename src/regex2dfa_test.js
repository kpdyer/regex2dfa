var regex2dfa = require('../.libs/regex2dfa.js');

var regex = "^(a|b)*$";
var actual_dfa = regex2dfa.regex2dfa(regex);
var expected_dfa = "0	0	97	97\n" +
                   "0	0	98	98\n" +
                   "0\n";

if (actual_dfa != expected_dfa) {
  console.warn("Test failed:");
  console.warn("-- ACTUAL");
  console.log(actual_dfa);
  console.warn("-- EXPECTED");
  console.log(expected_dfa);
} else {
  console.log("SUCCESS!");
}
