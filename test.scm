;#lang planet neil/sicp

(define (square x)
  (* x x))

(define (sum-of-squares x y)
  (+ (square x) (square y)))

;Ex 1.3
(define (smallest-of-three? x y z)
  (and (<= x y) (<= x z)))

(define (sum-of-squares-two-largest x y z)
  (cond ((smallest-of-three? x y z) (sum-of-squares y z))
        ((smallest-of-three? y z x) (sum-of-squares z x))
        (else (sum-of-squares x y))))


(define (sqrt-iter guess x)
  (if (good-enough? guess x)
      guess
      (sqrt-iter (improve guess x)
                 x)))

(define (improve guess x)
  (average guess (/ x guess)))

(define (average x y)
  (/ (+ x y) 2))

(define (good-enough? guess x)
  (< (abs (- (square guess) x)) 0.001))

(define (sqrt x)
  (sqrt-iter 1.0 x))



(define (f key a-list)
    (cdr (assq key a-list)))
