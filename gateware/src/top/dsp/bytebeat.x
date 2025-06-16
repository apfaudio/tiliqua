import std;

const CLOCK_HZ = u32:60000000;
const AUDIO_HZ = u32:48000;
const BYTEBEAT_HZ = u32:8000;
const CLOCK_TO_BYTEBEAT_RATIO = CLOCK_HZ / BYTEBEAT_HZ;
const CLOCK_TO_AUDIO_RATIO = CLOCK_HZ / AUDIO_HZ;
const_assert!(CLOCK_TO_BYTEBEAT_RATIO == u32:7500);
const DIV_WIDTH = std::clog2(CLOCK_TO_BYTEBEAT_RATIO);
const RATE_WIDTH = std::clog2(CLOCK_TO_AUDIO_RATIO);
const_assert!(DIV_WIDTH == u32:13);

struct ByteBeatState {
  a: u4,
  b: u4,
  c: u4,
  d: u4,
  t: u16,
  div: uN[DIV_WIDTH],
  rate: uN[RATE_WIDTH],
}

proc bytebeat {
  a_r: chan<u4> in;
  b_r: chan<u4> in;
  c_r: chan<u4> in;
  d_r: chan<u4> in;
  output_s: chan<u8> out;

  init {
    ByteBeatState{a: u4:5, b: u4:7, c: u4:3, d: u4:10, t: u16:0, div: uN[DIV_WIDTH]:0, rate: uN[RATE_WIDTH]:0}
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
    let div = state.div;
    let div_done = div == CLOCK_TO_BYTEBEAT_RATIO as uN[DIV_WIDTH];
    let div = if div_done {
      uN[DIV_WIDTH]:0
    } else {
      div + uN[DIV_WIDTH]:1
    };
    let rate = state.rate;
    let rate_done = rate == CLOCK_TO_AUDIO_RATIO as uN[RATE_WIDTH];
    let rate = if rate_done {
      uN[RATE_WIDTH]:0
    } else {
      rate + uN[RATE_WIDTH]:1
    };
    let t = if div_done {
      t + u16:1
    } else {
      t
    };
    send_if(tok, output_s, rate_done, s as u8);
    ByteBeatState{a, b, c, d, t, div, rate}
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
