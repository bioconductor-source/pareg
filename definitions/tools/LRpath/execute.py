"""
Python reimplementation of the original LRPath R code
"""

import sys

import numpy as np
import pandas as pd

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.tools.sm_exceptions import PerfectSeparationError

from utils import Executor


class MyExecutor(Executor):
    def setup(self):
        self.genes = self.df_inp.set_index('gene').to_dict()['p_value']
        self.grouping = self.df_terms.groupby('term')['gene'].apply(set).to_dict()

    def execute(self):
        results = []
        for term, gset in self.grouping.items():
            # print(self.genes, term, gset)

            df = pd.DataFrame({
                'y': np.array([1
                               if g in gset
                               else 0
                               for g in self.genes.keys()]),
                'X': -np.log10(np.array(list(self.genes.values())))
            })
            # print(df)

            logit = sm.genmod.families.links.logit()
            fam = sm.families.Binomial(link=logit)
            model = smf.glm('y ~ X', data=df, family=fam)

            fit = model.fit()

            # print(fit.summary())
            results.append({
                'term': term,
                'log_odds': fit.params['X'],
                'p_value': fit.pvalues['X']
            })

        df_res = pd.DataFrame(results)
        self.df_result = df_res[['term', 'p_value']].copy()


if __name__ == '__main__':
    ex = MyExecutor(sys.argv[1], sys.argv[2])
    ex.run()
