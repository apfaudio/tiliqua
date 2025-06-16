// Copyright 2023 Google LLC.
// SPDX-License-Identifier: Apache-2.0

struct ByteBeatState {
  a: u4,
  b: u4,
  c: u4,
  d: u4,
  t: u16,
}

proc bytebeat {
  a_r: chan<u4> in;
  b_r: chan<u4> in;
  c_r: chan<u4> in;
  d_r: chan<u4> in;
  output_s: chan<u8> out;

  init {
    ByteBeatState{a: u4:5, b: u4:7, c: u4:3, d: u4:10, t: u16:0}
  }

  config(a_r: chan<u4> in, b_r: chan<u4> in, c_r: chan<u4> in, d_r: chan<u4> in, output_s: chan<u8> out) {
    (a_r, b_r, c_r, d_r, output_s)
  }

  next(tok: token, state: ByteBeatState) {
    let (tok_a, a, _) = recv_non_blocking(tok, a_r, state.a);
    let (tok_b, b, _) = recv_non_blocking(tok, b_r, state.b);
    let (tok_c, c, _) = recv_non_blocking(tok, c_r, state.c);
    let (tok_d, d, _) = recv_non_blocking(tok, d_r, state.d);
    let tok = join(tok_a, tok_b, tok_c, tok_d);
    let t = state.t;
    let s = ((t*a as u16)&(t>>b as u16))|((t*c as u16)&(t>>d as u16));
    send(tok, output_s, s as u8);
    ByteBeatState{a: a, b: b, c: c, d: d, t: t + u16:1}
  }
}

#[test_proc]
proc bytebeat_test {
  terminator: chan<bool> out;
  a_s: chan<u4> out;
  a_r: chan<u4> in;
  b_s: chan<u4> out;
  b_r: chan<u4> in;
  c_s: chan<u4> out;
  c_r: chan<u4> in;
  d_s: chan<u4> out;
  d_r: chan<u4> in;
  output_s: chan<u8> out;
  output_r: chan<u8> in;

  init {
    ()
  }

  config(t: chan<bool> out) {
    let (a_s, a_r) = chan<u4>;
    let (b_s, b_r) = chan<u4>;
    let (c_s, c_r) = chan<u4>;
    let (d_s, d_r) = chan<u4>;
    let (output_s, output_r) = chan<u8>;
    spawn bytebeat(a_r, b_r, c_r, d_r, output_s);
    (t, a_s, a_r, b_s, b_r, c_s, c_r, d_s, d_r, output_s, output_r)
  }

  next(tok: token, state: ()) {
    let (tok, pcm) = for (i, (tok, pcm)) in u16:0..u16:0x1ff {
      let (tok, sample) = recv(tok, output_r);
      (tok, update(pcm, i, sample))
    }((tok, u8[0x200]:[0, ...]));
    send(tok, terminator, true);
    trace!(pcm);
 }
}
