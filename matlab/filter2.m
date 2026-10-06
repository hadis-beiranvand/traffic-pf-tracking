function FF=filter2(F,fr,num)



    b=[];
    A =F;

    I   = double(rgb2gray(F));
    Hsharpenning = [1 1 1;1 1 1; 1 1 1]/9;
    I = imfilter(I,Hsharpenning);
    I = round(I);
    
    load('inf.mat')  
    struct2vars(info.b(num))
    
    if info.b(num).flag==0
        imshow(uint8(F));      
        
        sq=40;
        
%         while(input('erer')==1)
%         [x0 y0] =  ginput(1)
%         [x1 y1] =  ginput(1)
%         end
        m=0.775085;
        m1=-0.8130;
        x0=m*(pxn)+130-sq;x1=m*(pxn)+130+sq;
        y0=m1*(pyn)+890+sq;y1=m1*(pyn)+890-sq;
%         num
%         plot(x1,y1,'MarkerFaceColor','r','MarkerSize',10+5)
        qs=[x0 y0 x1 y1];
        e=length(find(qs<90 | qs> 910));
        if e==0
        info.b(num).flag=1;
        if x0>x1
            mm=x1;x1=x0;x0=mm;
        end
        if y0>y1
            mm=y1;y1=y0;y0=mm;
        end
        tic
        info.b(num).x0      = round(x0);
        info.b(num).y0      = round(y0);
        info.b(num).x1      = round(x1);
        info.b(num).y1      = round(y1);
        
        Xr  = x1;
        Xl  = x0;
        Yt  = y0;
        Yb  = y1;
        
        xc      = round((x0+x1)/2);
        yc      = round((y0+y1)/2);
        Wt      = x1-x0+1;
        Ht      = y1-y0+1;
        HHt     = round(Ht/2);
        WWt     = round(Wt/2);
        Ht      = 2*HHt+1;
        Wt      = 2*WWt+1;
        Variance_u = WWt*20;
        Variance_v = HHt*20;
        T = I(yc-HHt:yc+HHt,xc-WWt:xc+WWt);
        out = Epac(2*HHt+1,2*WWt+1);
        Tmodel  = Q(xc,yc,out,T,Ht,Wt);
        t = toc;
        t(fr)= t;
        e       = 33;
        c       = 0;
        g       = out;
        g(:,:)  = 1;
        
        
        info.b(num).Ht=Ht;
        info.b(num).HHt=HHt;
        info.b(num).Wt=Wt;
        info.b(num).WWt=WWt;
        info.b(num).out=out;
        info.b(num).T=T;
        info.b(num).xc=xc;
        info.b(num).yc=yc;
        info.b(num).Variance_u=Variance_u;
        info.b(num).Variance_v=Variance_v;
        info.b(num).Tmodel=Tmodel;
        info.b(num).t=t;
        info.b(num).e=e;
        info.b(num).c=c;
        info.b(num).g=g;
%         info.b(num).a=5;
        
        
%         inf.g.h2=h2;
%         info.b(num)=b;
        save('inf.mat','info');
%Track ==================================================================
        end
        FF=F;
    else
        load('inf.mat');
        struct2vars(info.b(num))
        struct2vars(info.g)
        
%         disp(size(Ht))

      tic
        %===============================
        Cr            = zeros(Ht,3);
        Cl            = zeros(Ht,3);
        Ct            = zeros(3,Wt);
        Cb            = zeros(3,Wt);
        %===============================
        Cl(:,1)       = -2;        Cr(:,1)      =  2;
        Cl(:,2)       = -1;        Cr(:,2)      = -1;
        Cl(:,3)       =  2;        Cr(:,3)      = -2;

        Ct(1,:)       = -2;        Cb(1,:)      =  2;
        Ct(2,:)       = -1;        Cb(2,:)      = -1;
        Ct(3,:)       =  2;        Cb(3,:)      = -2;
         
        %===============================

        MML = -10e10;  MMR = -10e10;
        MMT = -10e10;  MMB = -10e10;
        %===============================
      M = 0.1;
      k = 0;
   for i=1:N
         u(i) = sqrt(Variance_u)*randn(1,1);
         v(i) = sqrt(Variance_v)*randn(1,1);
         x(i) = xc + u(i);
         y(i) = yc + v(i);             
       while ((x(i)>im_width-WWt)||(x(i)<1+WWt))
         u(i) = sqrt(Variance_u)*randn(1,1);
         x(i) = xc + u(i);
       end
       while ((y(i)>im_height-HHt)||(y(i)<1+HHt))
         v(i) = sqrt(Variance_v)*randn(1,1);
         y(i) = yc + v(i);             %!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       end
   end
%Max&Min ==================================================================
Max_x = max(x);
Min_x = min(x);
Max_y = max(y);
Min_y = min(y);
Variance_x0 = Max_x - Min_x;
Variance_y0 = Max_y - Min_y;
Variance_x = Variance_x0;
Variance_y = Variance_y0;
 %Iteration==============================================================
 while ((Variance_x >= (Variance_x0/4))&& (Variance_y >= (Variance_y0/4)))
     k = k + 1;
        for i=1:N
            C = I(round(y(i))-HHt:round(y(i))+HHt,round(x(i))-WWt:round(x(i))+WWt);           
            Cmodel(i) = P(x(i),y(i),out,C,Ht,Wt);
            W(i) = Weight(Cmodel(i).his,Tmodel.his,M);
        end
%        Normalize the likelihood of each a priori estimate.=========
         qsum = sum(W);
         for i = 1 : N
            W(i) = W(i) / qsum;
         end
 %       Resampling================================================== 
         for i = 1 : N
            uu = rand; % uniform random number between 0 and 1
            qtempsum = 0;
            for j = 1 : N
                qtempsum = qtempsum + W(j);
                if qtempsum >= uu
                    x(i) = Cmodel(j).xc;
                    y(i) = Cmodel(j).yc;
                   break;
                end
            end
         end
         Max_x = max(x);
         Min_x = min(x);
         Max_y = max(y);
         Min_y = min(y);
         Variance_x = Max_x - Min_x;
         Variance_y = Max_y - Min_y;
         Variance_u = WWt*10;
         Variance_v = HHt*10;
         %N = 40;
%          if k >= 7
%              Variance_u =im_width^2;
%              Variance_v =im_height^2;
%              N = 200;
%              break;
%          end
     %end%end of iteration
     Iteration(fr) = k;
 end
%=========================================================================
          xc = mean(x);
          yc = mean(y);
          xc = round(xc);
          yc = round(yc);
          C  = I(yc-HHt:yc+HHt,xc-WWt:xc+WWt);
          Cmodel = P(xc,yc,out,C,Ht,Wt);
          W1 = Weight1(Tmodel.his,Cmodel.his,I);
          while((c<10)&&(e>0.5))
            [e yc xc] = Iteration1(yc,xc,Ht,Wt,W1,g);
            c         = c+1;
            C         = I(yc-HHt:yc+HHt,xc-WWt:xc+WWt);
            Cmodel    = P(xc,yc,out,C,Ht,Wt);
            W1        = Weight1(Tmodel.his,Cmodel.his,I);
          end
 %======================================================================       
        LXl = round(xc-WWt-0.2*Wt);   TXl = round(xc-WWt+0.2*Wt);
        LXr = round(xc+WWt-0.2*Wt);   TXr = round(xc+WWt+0.2*Wt);
        LYt = round(yc-HHt-0.2*Ht);   TYt = round(yc-HHt+0.2*Ht);
        LYb = round(yc+HHt-0.2*Ht);   TYb = round(yc+HHt+0.2*Ht);
        %LEFT====================================
        
        for x=LXl:TXl
            CCL = 0;
            for i=-HHt:HHt
                for j=-1:1
                    CCL = CCL+Cl(i+HHt+1,j+2)*W1(i+yc,max(j+x,1));
                end
            end
            if CCL>MML
                MML = CCL;
                Xl  = x;
            end
        end
        %RIGHT====================================

        for x=LXr:TXr
            CCR = 0;
            for i=-HHt:HHt
                for j=-1:1
                    CCR = CCR+Cr(i+HHt+1,j+2)*W1(i+yc,min(j+x,im_width));
                end
            end
            if CCR>MMR
                MMR = CCR;
                Xr  = x;
            end
        end
        %TOP======================================

        for y=LYt:TYt
            CCT = 0;
            for i=-1:1
                for j=-WWt:WWt
                    CCT = CCT+Ct(i+2,j+WWt+1)*W1(max(i+y,1),j+xc);
                end
            end
            if CCT>MMT
                MMT = CCT;
                Yt  = y;
            end
        end
        %BOTTOM===================================

        for y=LYb:TYb
            CCB = 0;
            for i=-1:1
                for j=-WWt:WWt
                    CCB = CCB+Cb(i+2,j+WWt+1)*W1(min(i+y,im_height),j+xc);
                end
            end
            if CCB>MMB
                MMB = CCB;
                Yb  = y;
            end
        end
        %==========================================
        e   = 33 ;
        c   = 0  ;
        HHHt = round((Yb-Yt)/2);
        WWWt = round((Xr-Xl)/2);
        if ((HHHt<50)&&(HHHt>7))
            if ((HHHt<(1.5*HHt))||(HHHt>(0.8*HHt)))
                HHt = HHHt;
                Ht  = 2*HHt+1;
            end
        end
        if((WWWt<50)&&(WWWt<7))
            if ((WWWt<(1.5*WWt))||(WWWt>(0.8*WWt)))
                WWt = WWWt;
                Wt  = 2*WWt+1;
            end
        end

        %FFH(fr-SFrame)=Ht;
        %FFW(fr-SFrame)=Wt;
        %==========================================
        out = Epac(2*HHt+1,2*WWt+1);
%         T = I(yc-HHt:yc+HHt,xc-WWt:xc+WWt);
%         Tmodel  = Q(xc,yc,out,T,Ht,Wt);
        %EpaC    = CandidEpanechnikov(2*HHt+1,2*WWt+1);
        g       = out;
        g(:,:)  = 1;
       
        
        %===============================================
          t2 = toc;
          t(fr)= t2;
          A(1:2*HHt+1,1:2*WWt+1,:)       =           A(yc-HHt:yc+HHt,xc-WWt:xc+WWt,:)    ;
          A(yc-HHt:yc+HHt,xc-WWt,1)      = 255;      A(yc-HHt:yc+HHt,xc-WWt,2:3)      = 0;  
          A(yc-HHt:yc+HHt,xc,1)          = 255;      A(yc-HHt:yc+HHt,xc,2:3)          = 0;
          A(yc-HHt:yc+HHt,xc+WWt,1)      = 255;      A(yc-HHt:yc+HHt,xc+WWt,2:3)      = 0;
          A(yc-HHt,xc-WWt:xc+WWt,1)      = 255;      A(yc-HHt,xc-WWt:xc+WWt,2:3)      = 0;
          A(yc+HHt,xc-WWt:xc+WWt,1)      = 255;      A(yc+HHt,xc-WWt:xc+WWt,2:3)      = 0;
          A(yc-10:yc+10,xc,2)            = 255;      A(yc-10:yc+10,xc,3)              = 0;     A(yc-10:yc+10,xc,1) = 0;
          A(yc,xc-10:xc+10,2)            = 255;      A(yc,xc-10:xc+10,3)              = 0;     A(yc,xc-10:xc+10,1) = 0;                        
          
 %Update_Tmodel============================================================
          CC = I(yc-HHt:yc+HHt,xc-WWt:xc+WWt);
          CCmodel = P(xc,yc,out,CC,Ht,Wt);
          Dist = distance(CCmodel.his,Tmodel.his);
          Distance(fr) = Dist;
%           if((Distance(fr)>=0.65) || (Distance(fr)<=0.1))
%               Tmodel.his = 0.9*Tmodel.his+0.1*CCmodel.his ;
%           end       
%==========================================================================
        info.b(num).x0      = x0;
        info.b(num).y0      = y0;
        info.b(num).x1      = x1;
        info.b(num).y1      = y1;      
        info.b(num).Ht=Ht;
        info.b(num).HHt=HHt;
        info.b(num).Wt=Wt;
        info.b(num).WWt=WWt;
        info.b(num).out=out;
        info.b(num).T=T;
        info.b(num).xc=xc;
        info.g.t(num,fr)=t2;
        info.g.Iteration(num,fr)=k;
        info.b(num).yc=yc;
        info.b(num).Variance_u=Variance_u;
        info.b(num).Variance_v=Variance_v;
        info.b(num).Tmodel=Tmodel;
        info.b(num).t=t;
        info.b(num).e=e;
        info.b(num).c=c;
        info.b(num).g=g;
        
        
        if pxn<760 & pxn>240 & pyn>240 & pyn<760
            info.b(num).in=1;
        end
        if (pxn>760 | pxn<240 | pyn>760 | pyn<240) & info.b(num).p1==info.b(num).pe
            info.b(num).in=0;
        end    
        
        
        
        FF=F;
        save('inf.mat','info');
        if info.b(num).in==0 & info.b(num).gozar==0
          FF=uint8(A);
        end
%   xlabel(['Frame = ' , num2str(fr) ,'   Time = ' , num2str(t2) , '   Particle =  ' , num2str(N), '   Particle MeanShift' ]);    
    end
 
end
