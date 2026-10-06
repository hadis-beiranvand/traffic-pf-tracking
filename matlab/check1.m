function [a,b]=check1(p1,pxn,pyn,num)

load('inf.mat');


s=[700 300 pxn pxn;
   pyn pyn 700 300];
q=check(p1,pxn,pyn);
a=s(1,p1);
b=s(2,p1);


if q>1
    c=[info.b.p1];
    f=find(c==p1);
    f=f(f~=num);
    g=[info.b(f).pxn];
    g1=[info.b(f).pyn];
    s=[max(g) min(g) pxn pxn;
       pyn pyn max(g1) min(g1)];
    a=s(1,p1);
    b=s(2,p1);
end


end

