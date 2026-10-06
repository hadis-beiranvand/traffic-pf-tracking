function Ai()

load('inf.mat');
struct2vars(info.g)


for num=1:length(info.b)
   struct2vars(info.b(num)) 
   switch info.b(num).in
       case 0
           if info.b(num).vt==0
              [a,b]=check1(p1,pxn,pyn,num);
              if max([pxn-a pyn-b])>200
                  info.b(num).v=30;
                  info.b(num).a=0;
                  info.b(num).TT=1;
                  info.b(num).pox=info.b(num).pxn;
                  info.b(num).poy=info.b(num).pyn;
              end
           else
              if check3(pxn,pyn,num)==1
                  info.b(num).v=50;
                  info.b(num).a=0;
                  info.b(num).TT=0;
                  info.b(num).pox=info.b(num).pxn;
                  info.b(num).poy=info.b(num).pyn;
              else
              if check(p1,pxn,pyn)>1
                  [a,b]=check1(p1,pxn,pyn,num);
                  if max([pxn-a pyn-b])>200
                      info.b(num).a=-(vt^2)/(2*(abs(max([pxn-a pyn-b]))));
                      info.b(num).pox=info.b(num).pxn;
                      info.b(num).poy=info.b(num).pyn;
                      info.b(num).v=info.b(num).vt;
                      info.b(num).TT=0;
                  else
                      info.b(num).a=0;
                      info.b(num).pox=info.b(num).pxn;
                      info.b(num).poy=info.b(num).pyn;
                      info.b(num).v=0;
%                       info.b(num).vt=0;
                      info.b(num).TT=0;
                  end
              else
                  info.b(num).a=0;
                  info.b(num).pox=info.b(num).pxn;
                  info.b(num).poy=info.b(num).pyn;
                  info.b(num).v=35;
%                   info.b(num).vt=0;
                  info.b(num).TT=0;
              end
              end
           end
       case 1
           if check2(p1,pxn,pyn,q,num)==0
               info.b(num).v=0;
               info.b(num).a=0;
               info.b(num).TT=0;
               info.b(num).pox=info.b(num).pxn;
               info.b(num).poy=info.b(num).pyn;               
           else
               if info.b(num).gozar==0
                   info.b(num).pox=info.b(num).pxn;
                   info.b(num).poy=info.b(num).pyn;
                   info.b(num).TT=1;
               end
               info.b(num).gozar=1;
               info.b(num).v=40;
               info.b(num).a=0;
              
                
           end       
   end
   save('inf.mat','info'); 
    
end
















end