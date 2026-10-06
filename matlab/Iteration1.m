function [D,yc,xc] = Iteration(yc,xc,Ht,Wt,W1,g)
s      = zeros(2,1);
HHt    = round(Ht/2);
WWt    = round(Wt/2);
for i=1:Ht
    for j=1:Wt
        s = s + W1(yc-HHt+i,xc-WWt+j)*g(i,j)*[yc-HHt+i;xc-WWt+j];
    end
end
r=0;
for i=1:Ht
    for j=1:Wt
        r = r + W1(yc-HHt+i,xc-WWt+j)*g(i,j);
    end
end
Y1 = round(s/r);
D  = sqrt((Y1(1,1)-yc)^2+(Y1(2,1)-xc)^2);
yc = Y1(1,1);
xc = Y1(2,1);