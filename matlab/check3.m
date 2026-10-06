function q=check3(pxn,pyn,num)

load('inf.mat');
s=   [0   300  500 700;...
      700 1000 300 500;...
      300 500  0   300;...
      500 700  700 1000];

d=s(pxn>s(:,1) & pxn<s(:,2) & pyn>s(:,3) & pyn<s(:,4));

q=0;
if ~isempty(d) & info.b(num).p1==info.b(num).pe
    q=1;
end




end






