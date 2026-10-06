function qq=check2(p1,pxn,pyn,q,num)


load('inf.mat');
c=[info.b.in];
f=find(c==1);
f=f(f~=num);
c=[info.b.gozar];
f1=find(c==0);
for i=1:length(f1)
    f=f(f~=f1(i));
end

c=[info.b.q];
c=c(f);

k=0;
q1=cell2mat(q);

if info.b(num).gozar==1
    qq=1;
else
    for i=1:length(c)    
        g=cell2mat(c(i));
        for i1=1:length(g(:,1))
            for i2=1:length(q1(:,1))
                if (q1(i2,1)>=g(i1,2) || g(i1,1)>=q1(i2,2)) || (q1(i2,3)>=g(i1,4) || g(i1,3)>=q1(i2,4))
                    k=k;
                else
                    if p1==info.b(f(i)).p11 && (abs(pxn-info.b(f(i)).pxn)>=200 || abs(pyn-info.b(f(i)).pyn)>=200)
                        k=k;
                    else
                        k=k+1;
                    end
                end
            end
        end
    end
    if k==0
        qq=1;
    else
        qq=0;
    end
end


        
end