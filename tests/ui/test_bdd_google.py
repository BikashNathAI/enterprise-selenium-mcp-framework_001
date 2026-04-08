import pytest
from pytest_bdd import scenarios
from steps.google_search_steps import *

scenarios("../../features/google_search.feature")