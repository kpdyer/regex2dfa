var regex2dfa_func = Module.cwrap('_regex2dfa', 'number', ['number', 'number',
  'number', 'number'
]);

ab2str = function (buf) {
  return String.fromCharCode.apply(null, new Uint8Array(buf));
}

str2ab = function (str) {
  var buf = new Uint8Array(str.length);
  var bufView = new Uint8Array(buf.buffer);
  for (var i = 0; i < str.length; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf.buffer;
}

regex2dfa = function (regex) {
  var regex_ab = str2ab(regex);
  var regex_ab_len = regex_ab.byteLength;
  var ptr = Module._malloc(regex_ab_len);
  var regex_dh = new Uint8Array(Module.HEAPU8.buffer, ptr, regex_ab_len);
  regex_dh.set(new Uint8Array(regex_ab));

  var dfa_len = 8192;
  ptr = Module._malloc(dfa_len);
  var dfa_ab = new Uint8Array(Module.HEAPU8.buffer, ptr, dfa_len);
  ptr = Module._malloc(4);
  var dfa_len_ab = new Uint8Array(Module.HEAPU8.buffer, ptr, 4);
  var data = new Uint32Array([dfa_len]);
  dfa_len_ab.set(new Uint8Array(data.buffer));

  var ret = regex2dfa_func(
    regex_dh.byteOffset, regex_ab_len,
    dfa_ab.byteOffset, dfa_len_ab.byteOffset);

  if (ret != 0) {
    return null;
  }

  var dfa_length = (new Uint32Array(dfa_len_ab.buffer, dfa_len_ab.byteOffset,
    4))[0];
  var result = new Uint8Array(dfa_length);
  result.set(new Uint8Array(dfa_ab.buffer, dfa_ab.byteOffset, dfa_length));
  var retval = ab2str(result.buffer);

  Module._free(regex_dh.byteOffset);
  Module._free(regex_ab.byteOffset);
  Module._free(dfa_ab.byteOffset);
  Module._free(dfa_len_ab.byteOffset);
  Module._free(result.byteOffset);

  return retval;
}

if (typeof exports == 'undefined') {
  var exports = {};
}

exports.regex2dfa = regex2dfa;
