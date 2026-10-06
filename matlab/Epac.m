function [out] = Epac(h,w)

out = zeros(h,w);
h = floor(h/2);
w = floor(w/2);

for i=1:2*h+1
    for j=1:2*w+1
        d = ((i-h)/(h))^2 + ((j-w)/(w))^2;
        if(d<1)
            out(i,j) = 1-d;
        else
            out(i,j) = 0;
        end
    end
end
temp = sum(sum(out));
out = out/temp;