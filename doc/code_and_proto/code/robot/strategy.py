#coding:utf-8


MAP_BAOSHOU = {
    0:1,
    1:1,
    2:2,
    3:3,
    4:4,
    5:5,
    6:6,
    7:7,
    8:8,
    9:9,
    10:10,
}

MAP_PINGHENG = {
    0:2,
    1:2,
    2:2,
    3:3,
    4:4,
    5:5,
    6:6,
    7:7,
    8:8,
    9:9,
    10:10,
}

MAP_JIJIN = {
    0:3,
    1:3,
    2:3,
    3:3,
    4:4,
    5:5,
    6:6,
    7:7,
    8:8,
    9:9,
    10:10,
}


STRATEGY_BAOSHOU = {
    1: (lambda r,n: 50 - 5 * r.x + 5 * r.k, lambda r,n: 50 + 5 * r.x - 5 * r.k ,    lambda r,n: 5 * (1 - r.x + r.k), \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 8 * r.x + 1.5 * n,      lambda r,n : 80 + 20 * r.x + 20 * r.b * (1-r.x)),
    2: (lambda r,n: 55 - 5 * r.x + 5 * r.k, lambda r,n: 45 + 5 * r.x - 5 * r.k ,    lambda r,n: 5 * (1 - r.x + r.k) + n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 7 * r.x + 1.2 * n,      lambda r,n : 70 + 30 * r.x + 30 * r.b * (1-r.x)),
    3: (lambda r,n: 60 - 5 * r.x + 5 * r.k, lambda r,n: 40 + 5 * r.x - 5 * r.k ,    lambda r,n: 10 - 5 * r.x + 5 * r.k + 2 * n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 6 * r.x + 1 * n,        lambda r,n : 50 + 50 * r.x + 40 * r.b * (1-r.x)),
    4: (lambda r,n: 65 - 5 * r.x + 5 * r.k, lambda r,n: 35 + 5 * r.x - 5 * r.k ,    lambda r,n: 15 - 5 * r.x + 5 * r.k + 3 * n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 5 * r.x + 0.8 * n,      lambda r,n : 48 + 50 * r.x + 35 * r.b * (1-r.x)),
    5: (lambda r,n: 70 - 5 * r.x + 5 * r.k, lambda r,n: 30 + 5 * r.x - 5 * r.k ,    lambda r,n: 20 - 5 * r.x + 5 * r.k + 4 * n, \
                    lambda r,n: 20 * r.b * (1-r.x) + n + 5*r.b,             lambda r,n: 4 * r.x + 0.5 * n,      lambda r,n : 45 + 50 * r.x + 30 * r.b * (1-r.x)),
    6: (lambda r,n: 80 - 5 * r.x + 5 * r.k, lambda r,n: 20 + 5 * r.x - 5 * r.k ,    lambda r,n: 30 - 5 * r.x + 5 * r.k + 6 * n, \
                    lambda r,n: 20 * r.b * (1-r.x) + 2*n + 5*r.b + 5,       lambda r,n: 3 * r.x + 0.33 * n,     lambda r,n : 25 * r.x + 30),
    7: (lambda r,n: 92 - 5 * r.x + 5 * r.k, lambda r,n: 8 + 5 * r.x - 5 * r.k ,     lambda r,n: 40 - 3 * r.x + 5 * r.k + 8 * n, \
                    lambda r,n: 15 * r.b * (1-r.x) + 5*n + 5*r.b + 25,      lambda r,n: 2 * r.x + 0.2 * n,      lambda r,n : 15 * r.x + 10),
    8: (lambda r,n: 98 - 5 * r.x + 5 * r.k, lambda r,n: 2 + r.x -  r.k ,            lambda r,n: 50 + 5 * r.k + 10 * n, \
                    lambda r,n: 10 * r.b * (1-r.x) + 10*n + 5*r.b + 60,     lambda r,n: 1 * r.x + 0.1 * n,      lambda r,n : 10 * r.x + 5),
    9: (lambda r,n: 0,                      lambda r,n: 0,                          lambda r,n: 100, \
                    lambda r,n: 10 * r.b * (1-r.x) + 10*n + 5*r.b + 80,     lambda r,n: 0.8 * r.x + 0.066 * n,  lambda r,n : 5),
    10: (lambda r,n:0,                      lambda r,n: 0,                          lambda r,n: 100, \
                    lambda r,n:100,                                         lambda r,n: 0,                      lambda r,n : 0),

}


STRATEGY_PINGHENG = {
    2: (lambda r,n: 50 - 5 * r.x + 5 * r.k, lambda r,n: 50 + 5 * r.x - 5 * r.k ,    lambda r,n: 5 * (1 - r.x + r.k), \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 8 * r.x + 1.5 * n,      lambda r,n : 80 + 20 * r.x + 20 * r.b * (1-r.x)),
    3: (lambda r,n: 55 - 5 * r.x + 5 * r.k, lambda r,n: 45 + 5 * r.x - 5 * r.k ,    lambda r,n: 5 * (1 - r.x + r.k) + n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 7 * r.x + 1.2 * n,      lambda r,n : 70 + 30 * r.x + 30 * r.b * (1-r.x)),
    4: (lambda r,n: 60 - 5 * r.x + 5 * r.k, lambda r,n: 40 + 5 * r.x - 5 * r.k ,    lambda r,n: 10 - 5 * r.x + 5 * r.k + 2 * n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 6 * r.x + 1 * n,        lambda r,n : 50 + 50 * r.x + 40 * r.b * (1-r.x)),
    5: (lambda r,n: 65 - 5 * r.x + 5 * r.k, lambda r,n: 35 + 5 * r.x - 5 * r.k ,    lambda r,n: 15 - 5 * r.x + 5 * r.k + 3 * n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 5 * r.x + 0.8 * n,      lambda r,n : 48 + 50 * r.x + 35 * r.b * (1-r.x)),
    6: (lambda r,n: 70 - 5 * r.x + 5 * r.k, lambda r,n: 30 + 5 * r.x - 5 * r.k ,    lambda r,n: 20 - 5 * r.x + 5 * r.k + 4 * n, \
                    lambda r,n: 20 * r.b * (1-r.x) + n + 5*r.b,             lambda r,n: 4 * r.x + 0.5 * n,      lambda r,n : 45 + 50 * r.x + 30 * r.b * (1-r.x)),
    7: (lambda r,n: 80 - 5 * r.x + 5 * r.k, lambda r,n: 20 + 5 * r.x - 5 * r.k ,    lambda r,n: 30 - 5 * r.x + 5 * r.k + 6 * n, \
                    lambda r,n: 20 * r.b * (1-r.x) + 2*n + 5*r.b + 5,       lambda r,n: 3 * r.x + 0.33 * n,     lambda r,n : 25 * r.x + 30),
    8: (lambda r,n: 92 - 5 * r.x + 5 * r.k, lambda r,n: 8 + 5 * r.x - 5 * r.k ,     lambda r,n: 40 - 3 * r.x + 5 * r.k + 8 * n, \
                    lambda r,n: 15 * r.b * (1-r.x) + 5*n + 5*r.b + 25,      lambda r,n: 2 * r.x + 0.2 * n,      lambda r,n : 15 * r.x + 10),
    9: (lambda r,n: 98 - 5 * r.x + 5 * r.k, lambda r,n: 2 + r.x - r.k ,             lambda r,n: 50 + 5 * r.k + 10 * n, \
                    lambda r,n: 10 * r.b * (1-r.x) + 10*n + 5*r.b + 60,     lambda r,n: 1 * r.x + 0.1 * n,      lambda r,n : 10 * r.x + 5),
    10: (lambda r,n: 0,                     lambda r,n: 0,                          lambda r,n: 100, \
                    lambda r,n: 10 * r.b * (1-r.x) + 10*n + 5*r.b + 80,     lambda r,n: 0.8 * r.x + 0.066 * n,  lambda r,n : 5),

}

STRATEGY_JIJIN = {
    3: (lambda r,n: 50 - 5 * r.x + 5 * r.k, lambda r,n: 50 + 5 * r.x - 5 * r.k ,    lambda r,n: 5 * (1 - r.x + r.k), \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 8 * r.x + 1.5 * n,      lambda r,n : 80 + 20 * r.x + 20 * r.b * (1-r.x)),
    4: (lambda r,n: 55 - 5 * r.x + 5 * r.k, lambda r,n: 45 + 5 * r.x - 5 * r.k ,    lambda r,n: 5 * (1 - r.x + r.k) + n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 7 * r.x + 1.2 * n,      lambda r,n : 70 + 30 * r.x + 30 * r.b * (1-r.x)),
    5: (lambda r,n: 60 - 5 * r.x + 5 * r.k, lambda r,n: 40 + 5 * r.x - 5 * r.k ,    lambda r,n: 10 - 5 * r.x + 5 * r.k + 2 * n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 6 * r.x + 1 * n,        lambda r,n : 50 + 50 * r.x + 40 * r.b * (1-r.x)),
    6: (lambda r,n: 65 - 5 * r.x + 5 * r.k, lambda r,n: 35 + 5 * r.x - 5 * r.k ,    lambda r,n: 15 - 5 * r.x + 5 * r.k + 3 * n, \
                    lambda r,n: 20 * r.b * (1-r.x),                         lambda r,n: 5 * r.x + 0.8 * n,      lambda r,n : 48 + 50 * r.x + 35 * r.b * (1-r.x)),
    7: (lambda r,n: 70 - 5 * r.x + 5 * r.k, lambda r,n: 30 + 5 * r.x - 5 * r.k ,    lambda r,n: 20 - 5 * r.x + 5 * r.k + 4 * n, \
                    lambda r,n: 20 * r.b * (1-r.x) + n + 5*r.b,             lambda r,n: 4 * r.x + 0.5 * n,      lambda r,n : 45 + 50 * r.x + 30 * r.b * (1-r.x)),
    8: (lambda r,n: 80 - 5 * r.x + 5 * r.k, lambda r,n: 20 + 5 * r.x - 5 * r.k ,    lambda r,n: 30 - 5 * r.x + 5 * r.k + 6 * n, \
                    lambda r,n: 20 * r.b * (1-r.x) + 2*n + 5*r.b + 5,       lambda r,n: 3 * r.x + 0.33 * n,     lambda r,n : 25 * r.x + 30),
    9: (lambda r,n: 92 - 5 * r.x + 5 * r.k, lambda r,n: 8 + 5 * r.x - 5 * r.k ,     lambda r,n: 40 - 3 * r.x + 5 * r.k + 8 * n, \
                    lambda r,n: 15 * r.b * (1-r.x) + 5*n + 5*r.b + 25,      lambda r,n: 2 * r.x + 0.2 * n,      lambda r,n : 15 * r.x + 10),
    10: (lambda r,n: 98 - 5 * r.x + 5 * r.k, lambda r,n: 2 + r.x - r.k ,             lambda r,n: 50 + 5 * r.k + 10 * n, \
                    lambda r,n: 10 * r.b * (1-r.x) + 10*n + 5*r.b + 60,     lambda r,n: 1 * r.x + 0.1 * n,      lambda r,n : 10 * r.x + 5),

}


