% Sieve of Eratosthenes
primes(N) -> primes(lists:seq(3, N, 2), round(math:sqrt(N) + 0.5), [2]).
primes([First|Rest], Max, Result) when First < Max -> primes([X || X <- Rest, (X rem First) =/= 0], Max, [First|Result]);
primes([First|Rest], Max, Result) -> primes(Rest, Max, [First|Result]);
primes([], _Max, Result) -> lists:reverse(Result).
