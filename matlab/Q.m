
function [Q] = Q(xc,yc,g,T,Ht,Wt)

Q = struct('yc',0,'xc',0,'his',zeros(1,256));
Q.xc = xc;
Q.yc = yc;
for j=1:Ht
    for k=1:Wt
        Q.his(T(j,k)+1) = Q.his(T(j,k)+1)+ g(j,k);
    end
end

temp = sum(sum(Q.his));
Q.his = Q.his/temp;
Q;