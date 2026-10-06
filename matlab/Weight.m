function [out] = Weight(p,q,sigma)

C = 1/(sqrt(2*pi*sigma^2));
d = distance(p,q);
out = C*exp(-(d^2)/(2*sigma^2));

