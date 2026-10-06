function controler()


global TT pxn pyn i v info pox poy 

load('inf.mat')
for i=1:length(info.b)
    struct2vars(info.b(i))
    pxnn=pxn;
    pynn=pyn;
    TT=TT+1;
    info.b(i).TT=TT;
    if info.b(i).in==1
        switch info.b(i).pen
            case 1
                
            case 2
                if info.b(i).fl1==0 | info.b(i).fl2==0
                switch p11
                    case 1
                        if pxn<600  & info.b(i).fl1==0
                            p1=4;
                            pk1=-1*pk1;
                            pk2=-1*pk2;
                            komaki
                        end
                        if pyn<400
                            p1=2;
                            pk1=[-1;+1; 0; 0];
                            pk2=[ 0; 0;-1;+1];
                            komaki
                            info.b(i).fl2=1;
                        end
                    case 2 
                        if pxn>400 & info.b(i).fl1==0
                            p1=3;
                            pk1=-1*pk1;
                            pk2=-1*pk2;
                            komaki
                        end
                        if pyn>600
                            p1=1;
                            pk1=[-1;+1; 0; 0];
                            pk2=[ 0; 0;-1;+1];
                            komaki
                            info.b(i).fl2=1;
                        end
                    case 3 
                        if pyn<600 & info.b(i).fl1==0
                            p1=1;
                            pk1=-1*pk1;
                            pk2=-1*pk2;
                            komaki
                        end
                        if pxn>600
                            p1=4;
                            pk1=[-1;+1; 0; 0];
                            pk2=[ 0; 0;-1;+1];
                            komaki
                            info.b(i).fl2=1;
                        end
                    case 4 
                        if pyn>400 & info.b(i).fl1==0
                            p1=2;
                            pk1=-1*pk1;
                            pk2=-1*pk2;
                            komaki
                        end
                        if pxn<400
                            p1=3;
                            pk1=[-1;+1; 0; 0];
                            pk2=[ 0; 0;-1;+1];
                            komaki
                            info.b(i).fl2=1;
                        end
                end
                end
            case 3
                if info.b(i).fl1==0
                switch p1
                    case 1
                        if pxn<400
                            p1=3;                            
                            komaki
                        elseif info.b(i).gozar==1
                            poy=-(info.b(i).v/5)*TT+poy;
                        end
                    case 2 
                        if pxn>600
                            p1=4;
                            komaki
                        elseif info.b(i).gozar==1
                            poy=(info.b(i).v/5)*TT+poy;
                        end
                    case 3 
                        if pyn<400
                            p1=2;
                            komaki
                        elseif info.b(i).gozar==1
                            pox=(info.b(i).v/6)*TT+pox;
                        end
                    case 4 
                        if pyn>600
                            p1=1;
                            komaki
                        elseif info.b(i).gozar==1
                            pox=-(info.b(i).v/6)*TT+pox;
                        end
                end
                end            
            case 4
                if info.b(i).fl1==0
                switch p1
                    case 1
                        if pxn<600
                            p1=4;
                            komaki
                        end
                    case 2 
                        if pxn>400
                            p1=3;
                            komaki
                        end
                    case 3 
                        if pyn<600
                            p1=1;
                            komaki
                            
                        end
                    case 4 
                        if pyn>400
                            p1=2;
                            komaki
                        end
                end
                end
                
        end

        info.b(i).p1=p1;
        info.b(i).pk1=pk1;
        info.b(i).pk2=pk2;
        pxn=(1 / 2 * a * (TT) ^ 2 + v * (TT))*pk1(p1) + pox;
        pyn=(1 / 2 * a * (TT) ^ 2 + v * (TT))*pk2(p1) + poy;
        vt=a * TT + v;
    
    
    
        info.b(i).pxn=pxn;
        info.b(i).pyn=pyn;
        info.b(i).vt=vt;
    else
    pxn=(1 / 2 * a * TT ^ 2 + v * TT)*pk1(p1) + pox;
    pyn=(1 / 2 * a * TT ^ 2 + v * TT)*pk2(p1) + poy;
    vt=a * TT + v;
    
    info.b(i).pxn=pxn;
    info.b(i).pyn=pyn;
    info.b(i).vt=vt;
    end
    if vt<=0 & a~=0 & vt<v
        info.b(i).v=0;
        info.b(i).vt=0;
        info.b(i).a=0;
    end
    info.b(i).q=info.b(i).q1;
    dx=200;
    qq=[];
    if info.b(i).gozar==1
        q=cell2mat(info.b(i).q);
        qq=[];
        for ij=1:length(q(:,1))

            if pxn>=q(ij,1) & pxn<=q(ij,2) & pyn>=q(ij,3) & pyn<=q(ij,4)

                if info.b(i).pen==2
                    switch p1
                        case 1
                            qq=[qq; [pxn min([pxn+dx q(ij,2)]) q(ij,3) q(ij,4)]];
                        case 2
                            qq=[qq; [max([pxn-dx q(ij,1)]) pxn q(ij,3) q(ij,4)]];
                        case 3
                            qq=[qq; [q(ij,1)  q(ij,2) pyn min([pyn+dx q(ij,4)])]];
                        case 4
                            qq=[qq; [q(ij,1)  q(ij,2) max([pyn-dx q(ij,3)]) pyn]];
                    end
                else
                if info.b(i).pen==3 && info.b(i).p1~=info.b(i).p11 && ij==1 && length(q(:,1))==2
                    qq=[qq ;[]];
                    q1=cell2mat(info.b(i).q1);
                    q1(ij,:)=[];
                    info.b(i).q1={q1};
                else
                switch p1
                    case 1
                        qq=[qq; [max([pxn-dx q(ij,1)]) pxn q(ij,3) q(ij,4)]];
                    case 2
                        qq=[qq; [pxn min([pxn+dx q(ij,2)])  q(ij,3) q(ij,4)]];
                    case 3
                        qq=[qq; [q(ij,1)  q(ij,2) max([pyn-dx q(ij,3)]) pyn]];
                    case 4
                        qq=[qq; [q(ij,1)  q(ij,2) pyn min([pyn+dx q(ij,4)])]];
                end
                end
                end
            else
                qq=qq;
            end
        end
        
    else
        dx=dx*3/2;
        q=cell2mat(info.b(i).q);
        if  info.b(i).in==1
            switch p1
                case 1
                    qq=[max([pxn-dx q(1,1)]) pxn q(1,3) q(1,4)];
                case 2
                    qq=[pxn min([pxn+dx q(1,2)])  q(1,3) q(1,4)];
                case 3
                    qq=[q(1,1)  q(1,2) max([pyn-dx q(1,3)]) pyn];
                case 4
                    qq=[q(1,1)  q(1,2) pyn min([pyn+dx q(1,4)])];
            end
        end
    end
    if isempty(qq)
        info.b(i).q=info.b(i).q1;
    else
        info.b(i).q={qq};
    end
    if abs(pxnn-pxn)>=100 | abs(pynn-pyn)>=100
        info.b(i).v=50;
        info.b(i).vt=0;
        info.b(i).a=0;
    end
    
info.b(i).pnx=[info.b(i).pnx; sqrt(((info.b(i).pox1-pxn)^2)+((info.b(i).poy1 -pyn)^2))];
info.b(i).pny=[info.b(i).pny pyn];
end

save('inf.mat','info');


end





function komaki
    global v TT pxn pyn i info pox poy 
    TT=0;
    info.b(i).TT=0;
    pox=pxn;
    poy=pyn;
    v=info.b(i).vt;
    info.b(i).v=info.b(i).vt;
    info.b(i).pox=pxn;
    info.b(i).poy=pyn;
    info.b(i).fl1=1;
end

