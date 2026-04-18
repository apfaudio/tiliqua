# Contributing

As an open-source project we welcome contributions in all areas: to the DSP library, to Tiliqua's platform code, to the examples, to the Rust firmware - whatever piques your interest. As long as you're happy with your contribution falling under the same license as the project.

In short, contributions to Tiliqua can happen in 3 areas:
- Out-of-tree: you fork the repo, change some stuff, share the repo or bitstreams with people, keeping things open source but never merging your changes back.
    - You may file a pull request against [`tiliqua-webflash`](https://github.com/apfaudio/tiliqua-webflash) with a link to your source, and I would be happy to review the bitstream and test it, making it available to all users.
    - Here the review hurdle is 'it is interesting, it works and won't damage Tiliqua or user hardware' - the contribution rules below do not apply to out-of-tree contributions, beyond the code being reviewable and proven to work.
- In-tree toplevels: you make some changes to the included top-level bitstreams. Here the contribution rules below DO apply.
- In-tree shared libraries / hardware: you make changes to infrastructure shared between all Tiliqua projects. Here, the contribution rules below DO apply.

## Use of LLMs / AI in contributions

**This applies for any PRs against this repository.**

As part of NGI0 (see Funding below), please become familiar with [NLnet's AI policy](https://nlnet.nl/foundation/policies/generativeAI/). Below are some additional guidelines specific to this project.

**Put simply: any PR which looks completely AI-generated, especially where it is doubtful the author understands what they have changed / added, will be rejected.**

This project **does not accept** AI-assisted contributions in the following areas:
- All code shared amongst top-levels - such as DSP library code and platform drivers.
- Any top-level bitstreams used in tutorials and intented to be pedagogical (`dsp/top.py`).
- All documentation text.
- All hardware design and documentation.

This project **may accept** AI-assisted contributions **with clear provenance, which are reviewable and clearly explainable** in the following areas:
- Any top-level bitstreams not covered above.
- Test and simulation harnesses

Commit messages, PR titles and descriptions **must always be hand-written**. In addition to [NLnet's AI policy](https://nlnet.nl/foundation/policies/generativeAI/), some points borrowed from `betrusted-io/xous-core`:

    - When you submit a contribution, you represent that you are the author and that you are fully accountable for the entirety of the contribution.
    - You are responsible for your contribution, including vouching for the quality, license compliance, and utility of your submission.
    - Using AI assistance in your contribution does not relieve you of the responsibility to ensure that your contribution meets project standards; your contributions must be modular, reviewable, and clearly explainable.
