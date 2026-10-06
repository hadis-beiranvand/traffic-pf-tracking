function [d] = distance(p,q)
d = 0;
bhatt = 0;
for i=1:256
    bhatt = bhatt + sqrt(p(i) * q(i));
end

d = sqrt(1-bhatt);