% shell driver for sieve.hrl
-module(sieve).
-export([main/1]).
-include("sieve.hrl").

main([A])->
    Print = fun(X) -> io:format("~p ",[X]) end,
    Primes = primes(list_to_integer(atom_to_list(A))),
    lists:foreach(Print, Primes),
    io:format("~n"),
    init:stop().
