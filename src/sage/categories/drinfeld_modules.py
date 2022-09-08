r"""
Drinfeld modules over a base

This module provides the class
:class:`sage.category.drinfeld_modules.DrinfeldModules`.

AUTHORS:

- Antoine Leudière (2022-04)
- Xavier Caruso (2022-06)
"""

#*****************************************************************************
#  Copyright (C) 2022      Xavier Caruso <xavier.caruso@normalesup.org>
#                          Antoine Leudière <antoine.leudiere@inria.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category import CategoryWithParameters
from sage.categories.homsets import Homsets
from sage.misc.functional import log
from sage.misc.latex import latex
from sage.rings.integer import Integer
from sage.rings.morphism import RingHomomorphism
from sage.rings.polynomial.ore_polynomial_ring import OrePolynomialRing
from sage.rings.polynomial.polynomial_ring import PolynomialRing_general


class DrinfeldModules(CategoryWithParameters):
    r"""
    This class represents the category of Drinfeld modules on a given
    base.

    The category is uniquely defined by its base, which is a ring
    morphism from the function ring `\Fq[X]` to a field `K`. Note that
    the base is a morphism, but not a field. The base is often denoted
    `\gamma`, and we call `K` an *`\Fq[X]-field`*.

    The monic polynomial that generates the kernel of the base is called
    the *`\Fq[X]`-characteristic of the `\Fq[X]`-field `K`*.

    .. NOTE::

        These notations will be used throughout this documentation.

    We say that `\Fq[X]` is the *function ring of the category*;
    *K\{\tau\}* is the *Ore polynomial ring of the category*; `t` is the
    *Ore variable of the category*. The *constant coefficient of the
    category* is the image of `X` under the base. The
    `\Fq[X]`-characteristic of the `\Fq[X]`-field `K` can also be
    referred to as its *function ring-characteristic*.

    INPUT: the base, a ring morphism

    .. RUBRIC:: Construction

    Generally, Drinfeld modules objects are created before their
    category, and the category is retrieved as an attribute of the
    Drinfeld module::

        sage: Fq = GF(11)
        sage: FqX.<X> = Fq[]
        sage: K.<z> = Fq.extension(4)
        sage: p_root = z^3 + 7*z^2 + 6*z + 10
        sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
        sage: cat = phi.category()
        sage: cat
        Category of Drinfeld modules defined over base Ring morphism:
          From: Univariate Polynomial Ring in X over Finite Field of size 11
          To:   Finite Field in z of size 11^4
          Defn: X |--> z^3 + 7*z^2 + 6*z + 10

    The output tells the user that the category is only defined by its
    base.

    .. RUBRIC:: Properties of the category

    The base, which is a morphism, is retrieved using the method
    :meth:`morphism`::

        sage: cat.base()
        Ring morphism:
          From: Univariate Polynomial Ring in X over Finite Field of size 11
          To:   Finite Field in z of size 11^4
          Defn: X |--> z^3 + 7*z^2 + 6*z + 10

    The so-called *constant coefficient* --- which is the same for all
    Drinfeld modules in the category --- is simply the image of `X` by
    this morphism:

        sage: cat.constant_coefficient()
        z^3 + 7*z^2 + 6*z + 10
        sage: cat.base()(X) == cat.constant_coefficient()
        True

    Similarly, the *function ring-characteristic* of the category is either
    `0` or the unique monic polynomial in `\Fq[X]` that generates
    the kernel of the base::

        sage: cat.characteristic()
        X^2 + 7*X + 2
        sage: cat.base()(cat.characteristic())
        0

    The base, function ring and Ore polynomial ring are the
    same for the category and its objects::

        sage: cat.base() is phi.base()
        True

        sage: cat.function_ring() is phi.function_ring()
        True
        sage: cat.function_ring()
        Univariate Polynomial Ring in X over Finite Field of size 11
        sage: cat.function_ring() is cat.base().domain()
        True

        sage: cat.ore_polring() is phi.ore_polring()
        True
        sage: cat.ore_polring()
        Ore Polynomial Ring in t over Finite Field in z of size 11^4 twisted by z |--> z^11

    .. RUBRIC:: Creating Drinfeld module objects from the category

    Calling :meth:`object` with an Ore polynomial creates a Drinfeld module
    object in the category whose generator is the input::

        sage: psi = cat.object([p_root, 1])
        sage: psi
        Drinfeld module defined by X |--> t + z^3 + 7*z^2 + 6*z + 10 over base Ring morphism:
          From: Univariate Polynomial Ring in X over Finite Field of size 11
          To:   Finite Field in z of size 11^4
          Defn: X |--> z^3 + 7*z^2 + 6*z + 10
        sage: psi.category() is cat
        True

    Of course, the constant coefficient of the input must be the same as
    the category'::

        sage: cat.object([z, 1])
        Traceback (most recent call last):
        ...
        ValueError: constant coefficient must be the generator of the morphism that defines the category

    It is also possible to create a random object in the category. The
    input is the desired rank::

        sage: rho = cat.random_object(2)
        sage: rho  # random
        Drinfeld module defined by X |--> (7*z^3 + 7*z^2 + 10*z + 2)*t^2 + (9*z^3 + 5*z^2 + 2*z + 7)*t + z^3 + 7*z^2 + 6*z + 10 over Finite Field in z of size 11^4
        sage: rho.rank() == 2
        True
        sage: rho.category() is cat
        True

    TESTS:

        sage: Fq = GF(11)
        sage: FqX.<X> = Fq[]
        sage: K.<z> = Fq.extension(4)
        sage: from sage.categories.drinfeld_modules import DrinfeldModules
        sage: base = Hom(FqX, K)(0)
        sage: cat = DrinfeldModules(base)
        Traceback (most recent call last):
        ...
        ValueError: base must be a non zero morphism

        sage: base = Hom(FqX, FqX)(1)
        sage: cat = DrinfeldModules(base)
        Traceback (most recent call last):
        ...
        TypeError: base codomain must be a field

        sage: base = 'I hate Rostropovitch'
        sage: cat = DrinfeldModules(base)  # known bug (blankline)
        <BLANKLINE>
        Traceback (most recent call last):
        ...
        TypeError: input must be a ring morphism

        sage: ZZT.<T> = ZZ[]
        sage: base = Hom(ZZT, K)(1)
        sage: cat = DrinfeldModules(base)  # known bug (blankline)
        <BLANKLINE>
        Traceback (most recent call last):
        ...
        TypeError: function ring base must be a finite field
    """

    def __init__(self, base, name='t'):
        # Check input is a ring Morphism
        if not isinstance(base, RingHomomorphism):
            raise TypeError('input must be a Ring morphism')
        self._base = base
        self._function_ring = base.domain()
        # Check domain of base is Fq[X]
        function_ring = self._function_ring
        if not isinstance(function_ring, PolynomialRing_general):
            raise NotImplementedError('function ring must be a polynomial '
                                      'ring')
        function_ring_base = function_ring.base_ring()
        if not function_ring_base.is_field() \
                or not function_ring_base.is_finite():
            raise TypeError('function ring base must be a finite field')
        Fq = function_ring_base
        FqX = function_ring
        X = FqX.gen()
        # Check codomain of base is a field
        K = base.codomain()
        if not K.is_field():
            raise TypeError('base codomain must be a field')
        # Check base is a non zero morphism
        if base(X).is_zero():
            raise ValueError('base must be a non zero morphism')
        # Build K{t}
        d = log(Fq.cardinality(), Fq.characteristic())
        tau = K.frobenius_endomorphism(d)
        self._ore_polring = OrePolynomialRing(K, tau, names=name,
                                              polcast=False)
        # Create constant coefficient
        self._constant_coefficient = base(X)
        # Create characteristic
        self._characteristic = None
        if K.is_finite():
            f = base * FqX.coerce_map_from(Fq)  # Fq -> K
            E = K.over(f)
            self._characteristic = FqX(E(base(X)).minpoly())
        elif FqX.is_subring(K):
            self._characteristic = Integer(0)

    # Somehow required for the class definition
    def _make_named_class_key(self, name):
        return self._function_ring.category()

    def _latex_(self):
        r"""
        Return a latex representation of the category

        OUTPUT: a string

        EXAMPLE:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: latex(cat)
            \text{Category{ }of{ }Drinfeld{ }modules{ }defined{ }over{ }base{ }\begin{array}{l}
            \text{\texttt{Ring{ }morphism:}}\\
            \text{\texttt{{ }{ }From:{ }Univariate{ }Polynomial{ }Ring{ }in{ }X{ }over{ }Finite{ }Field{ }of{ }size{ }11}}\\
            \text{\texttt{{ }{ }To:{ }{ }{ }Finite{ }Field{ }in{ }z{ }of{ }size{ }11{\char`\^}4}}\\
            \text{\texttt{{ }{ }Defn:{ }X{ }|{-}{-}>{ }z{\char`\^}3{ }+{ }7*z{\char`\^}2{ }+{ }6*z{ }+{ }10}}
            \end{array}
        """
        return f'\\text{{Category{{ }}of{{ }}Drinfeld{{ }}modules{{ }}' \
               f'defined{{ }}over{{ }}base{{ }}{latex(self._base)}'

    def _repr_(self):
        r"""
        Return a string representation of the category

        OUTPUT: a string

        EXAMPLE:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: cat
            Category of Drinfeld modules defined over base Ring morphism:
              From: Univariate Polynomial Ring in X over Finite Field of size 11
              To:   Finite Field in z of size 11^4
              Defn: X |--> z^3 + 7*z^2 + 6*z + 10
        """
        return f'Category of Drinfeld modules defined over base {self._base}'

    # Somehow required for the class definition
    def Homsets(self):
        return Homsets()

    # Somehow required for the class definition
    def Endsets(self):
        return Homsets()

    def base(self):
        r"""
        Return the base of the category.

        OUTPUT: a ring morphism

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: base = cat.base()
            sage: base
            Ring morphism:
              From: Univariate Polynomial Ring in X over Finite Field of size 11
              To:   Finite Field in z of size 11^4
              Defn: X |--> z^3 + 7*z^2 + 6*z + 10
            sage: base(X) == cat.constant_coefficient()
            True
        """
        return self._base

    def characteristic(self):
        r"""
        Return the function ring-characteristic of the category.

        OUTPUT: `0` or a monic prime polynomial in the function ring

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: cat.characteristic()
            X^2 + 7*X + 2

            sage: L = Frac(FqX)
            sage: psi = DrinfeldModule(FqX, [L.gen(), 1])
            sage: psi
            Drinfeld module defined by X |--> t + X over base Ring morphism:
              From: Univariate Polynomial Ring in X over Finite Field of size 11
              To:   Fraction Field of Univariate Polynomial Ring in X over Finite Field of size 11
              Defn: X |--> X
            sage: fox = psi.category()
            sage: fox.characteristic()
            0
        """
        if self._characteristic is None:
            raise NotImplementedError
        return self._characteristic

    def constant_coefficient(self):
        r"""
        Return the constant coefficient of the category.

        OUTPUT: an element in the base codomain

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: cat.constant_coefficient()
            z^3 + 7*z^2 + 6*z + 10
            sage: cat.constant_coefficient() == cat.base()(X)
            True
        """
        return self._constant_coefficient

    def function_ring(self):
        r"""
        Return the function ring of the category.

        OUTPUT: a univariate polynomial ring

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: cat.function_ring()
            Univariate Polynomial Ring in X over Finite Field of size 11
            sage: cat.function_ring() is FqX
            True
        """
        return self._function_ring

    def object(self, gen):
        r"""
        Return a Drinfeld module object in the category whose generator
        is the input.

        INPUT: the generator of the Drinfeld module, given as an Ore
        polynomial or a list of coefficients

        OUTPUT: a Drinfeld module in the category

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: psi = cat.object([p_root, 0, 1])
            sage: psi
            Drinfeld module defined by X |--> t^2 + z^3 + 7*z^2 + 6*z + 10 over base Ring morphism:
              From: Univariate Polynomial Ring in X over Finite Field of size 11
              To:   Finite Field in z of size 11^4
              Defn: X |--> z^3 + 7*z^2 + 6*z + 10
            sage: t = phi.ore_variable()
            sage: cat.object(t^3 + z^3 + 7*z^2 + 6*z + 10) is phi
            True
        """
        from sage.rings.function_field.drinfeld_modules.drinfeld_module import DrinfeldModule
        # If gen is not in the Ore polring, an exception is raised
        gen = self._ore_polring(gen)
        X = self._function_ring.gen()
        base = self._base
        if gen[0] != base(X):
            raise ValueError('constant coefficient must be the generator '
                             'of the morphism that defines the category')
        return DrinfeldModule(self._function_ring, gen)

    def ore_polring(self):
        r"""
        Return the Ore polynomial ring of the category.

        OUTPUT: an Ore polynomial ring

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: cat.ore_polring()
            Ore Polynomial Ring in t over Finite Field in z of size 11^4 twisted by z |--> z^11
            sage: cat.ore_polring() is phi.ore_polring()
            True
        """
        return self._ore_polring

    def ore_variable(self):
        r"""
        Return the Ore variable of the category.

        OUTPUT: an Ore polynomial

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: cat.ore_variable()
            t
            sage: cat.ore_variable() is phi.ore_variable()
            True
        """
        return self._ore_polring.gen()

    def random_object(self, rank):
        r"""
        Return a random Drinfeld module in the category, whose rank is
        the input.

        INPUT: an integer, the rank of the Drinfeld module

        OUTPUT: a Drinfeld module in the category

        EXAMPLES:

            sage: Fq = GF(11)
            sage: FqX.<X> = Fq[]
            sage: K.<z> = Fq.extension(4)
            sage: p_root = z^3 + 7*z^2 + 6*z + 10
            sage: phi = DrinfeldModule(FqX, [p_root, 0, 0, 1])
            sage: cat = phi.category()
            sage: psi = cat.random_object(3) # random
            Drinfeld module defined by X |--> (6*z^3 + 4*z^2 + 10*z + 9)*t^3 + (4*z^3 + 8*z^2 + 8*z)*t^2 + (10*z^3 + 3*z^2 + 6*z)*t + z^3 + 7*z^2 + 6*z + 10 over Finite Field in z of size 11^4
            sage: psi.rank() == 3
            True
        """
        if not isinstance(rank, Integer):
            raise TypeError('rank must be a positive integer')
        if rank <= 0:
            raise ValueError('rank must be a positive integer')

        K = self._base.codomain()
        coeffs = [self._constant_coefficient]
        for _ in range(rank-1):
            coeffs.append(K.random_element())
        dom_coeff = 0
        while dom_coeff == 0:
            dom_coeff = K.random_element()
        coeffs.append(dom_coeff)

        return self.object(coeffs)

    # Somehow required for the class definition
    def super_categories(self):
        return []

    # Somehow required for the class definition
    class ParentMethods:

        def characteristic(self):
            return self.category().characteristic()

    # Somehow required for the class definition
    class ElementMethods:
        pass
