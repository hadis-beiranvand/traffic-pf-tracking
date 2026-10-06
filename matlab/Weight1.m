function [W]   = Weight1(q,p,C)
[Height Width] = size(C);
W              = zeros(Height,Width);
for i=1:Height
    for j=1:Width
        if p(C(i,j)+1)
            W(i,j) = q(C(i,j)+1)/(p(C(i,j)+1)+q(C(i,j)+1));
%             if W(i,j)<= 0.5
%                 W(i,j)=0;
%             end
        end
    end
end