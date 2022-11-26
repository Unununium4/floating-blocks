# floating-blocks

Code for finding the minimum length of two ordered binary sets separated and patched
together with any set of zeros up to length g that can thus contain a set of any
combination of binary digits of length g

![example: Floating Blocks MLCS - 16cm x 4cm - BEV](/floating%20leaves.jpg)

# Physical Context

The two ordered binary sets in question represent collimator panels where we've arbitrarily
chosen a 0 value to represent the lack of a collimator blocking the beam, and a 1 to
represent the presence of a collimator blocking the beam.

In this context, we can assume the following:

- sequences with an ordered sequence of 0s at the beginning or end can be represented either
  by the collimator panel present with no collimator blocking the beam at those positions or
  by the lack of a collimator panel present at those locations, and these two states are
  mathematically indistinguishable
- due to the above, a long sequence of consecutive zeros on either end of the configuration
  can be represented equivalently as a problem using shorter sequences
- a gap between the two collimator panels can be represented as a contiguous sequence of 0s
  between the collimator panels

# Mathematical Problem Statement

Coming soon...
