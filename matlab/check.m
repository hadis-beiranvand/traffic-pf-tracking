function q=check(p1,pxn,pyn)
    
load('inf.mat');




switch p1
    case 1
        s=[700 pxn+20 500 700];
    case 2
        s=[pxn-20 300 300 500];
    case 3
        s=[300 500 700 pyn+20];
    case 4
        s=[500 700 pyn-20 300];
end

a=[info.b.pxn];
b=[info.b.pyn];


h=find(a>s(1) & a<s(2));
h1=find(b>s(3) & b<s(4));
q=sum(ismember(h,h1));



end



