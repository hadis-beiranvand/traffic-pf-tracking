function inputcar()

n=0;
c=0;

po=[5 1000];

p=[600 1000;400 0;1000 400;0 600];
pk1=[+1;-1; 0; 0];
pk2=[ 0; 0;+1;-1];
pend=[1 1 1;1 2 2;1 3 3;1 4 4;...
      2 2 1;2 1 2;2 4 3;2 3 4;...
      3 3 1;3 4 2;3 2 3;3 1 4;...
      4 4 1;4 3 2;4 1 3;4 2 4];

while c==0
    n=n+1;
   p1=input(strcat('please Enter Street of car',num2str(n),':1_4\n'));
   p2=input(strcat('please Enter position of car',num2str(n),':0_500\n'));
   
   e=length(find(po(:,1)==p1 & abs(po(:,2)-p2)<50));
   if e>0
      disp('positions is Repetitious')
      n=n-1;
   else    
   pe=input(strcat('please Enter goal Street of car',num2str(n),':1_4\n'));
   a=input(strcat('please Enter Acceleration of car',num2str(n),':0_5\n'));
   v=input(strcat('please Enter Initial Speed of car',num2str(n),':0_10\n'));
   s=input(strcat('please Enter size of car',num2str(n),':0_5\n'));
   pen=find(pend(:,1)==p1 & pend(:,2)==pe);
   
   po=[po;[p1 p2]];
       
   po1=p(p1,2)+(pk1(p1))*p2;
   po2=p(p1,1)+(pk2(p1))*p2;
   
   
   q=sakht(p1,pe);
    
   
   info2.b(n).q=q;
   info2.b(n).q1=q;
   info2.b(n).pox=po1;
   info2.b(n).pnx=[];
   info2.b(n).poy=po2;
   info2.b(n).pny=[];
   info2.b(n).p1=p1;
   info2.b(n).pe=pe;
   info2.b(n).pen=pend(pen,3);
   info2.b(n).s=s;
   info2.b(n).v=v;
   info2.b(n).a=a;
   info2.b(n).flag=0;
   info2.b(n).in=0;
   info2.b(n).fl1=0;
   info2.b(n).fl2=0;
   info2.b(n).pox1=po1;
   info2.b(n).poy1=po2;
   info2.b(n).pk1=[-1;+1; 0; 0];
   info2.b(n).pk2=[ 0; 0;-1;+1];
   info2.b(n).TT=0;
   info2.b(n).p11=p1;
   info2.b(n).gozar=0;
   
   
   
   
   if ~input('Do you have more car in your plan? 1/0')
        c=1;
   end
   
   end
end
save('inf2.mat','info2');


end