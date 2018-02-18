"""Functional functions"""
from itertools import chain

def flatmap(f, items):
  return list(chain.from_iterable(map(f, items)))

