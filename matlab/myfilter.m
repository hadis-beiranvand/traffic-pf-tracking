
close all
clear
clc


im_height = 1000;
im_width  = 1000;
SFrame = 1;
N = 100;
x=zeros(1,N);
y=zeros(1,N);
W = zeros(1,N);
W1 = zeros(1,N);
u = zeros(1,N); %noise           
v = zeros(1,N); %noise
t = zeros(1,N);
Iteration = zeros(1,N);
Distance = zeros(1,N);

inputcar();


load('inf2.mat')
load('inf.mat')
info=info2;

t=repmat(t,length(info.b),1);
Iteration=[];

g.N=N;
g.x=x;
g.y=y;
g.W=W;
g.W1=W1;
g.u=u;
g.v=v;
g.t=t;
g.Iteration=Iteration;
g.Distance=Distance;
g.im_width=im_width;
g.im_height=im_height;
g.pk1=[-1;+1; 0; 0];
g.pk2=[ 0; 0;-1;+1];
g.t=[];

info.g=g;

for i=1:length(info.b)
    info.b(i).pnx=[];
    info.b(i).pny=[];
end


save('inf.mat','info');


fr  = SFrame;
u=0;
while u==0
    
   fig= figure(1);
   set(fig,'position',[0 0 400 400]);
   hold off
   plotBGIMAGE(fr);
   
    
   F=imread('frame.jpg');
   F=imresize(F, [im_width im_height]);


    fig1= figure(2);
    set(fig1,'position',[450 138.3793 696 641.3793]);
    for num=1:length(info.b)
        F=filter2(F,fr,num);
    end
    imshow(F)
    xlabel(['Frame = ' , num2str(fr) ]);    
    
    Ai();
    
    fr=fr+1;
    cc=[info.b.gozar];
    f1=find(cc==0);
    cc=[info.b.in];
    f2=find(cc==1);
    if isempty(f2) & isempty(f1)
        u=1;
        break;
    end
end

a=[];
for i=1:length(info.b)
    a=[a;strcat('car',num2str(i))];
end

figure;
% subplot(2,1,1);
plot(SFrame:fr-1,info.g.t)
% legend(['With Adaptive Resampling And  ' , num2str(N),'  Particle']);
legend(a)
xlabel('Frame  ' );
ylabel('Time  ' );
% subplot(2,1,2);
figure;plot(SFrame:fr-1,info.g.Iteration)
% legend(['With Adaptive Resampling And  ' , num2str(N),'  Particle']);
legend(a)
xlabel('Frame  ' );
ylabel('Iteration  ' );


% c=repmat(SFrame:fr-1,6,1);
% figure;
% % subplot(2,1,1);
% stem(info.g.t,c)
% % legend([,'With Adaptive Resampling And  ' , num2str(N),'  Particle']);
% legend(a)
% ylabel('Frame  ' );
% xlabel('Time  ' );

% ff=[];ff1=[];
% for i=1:length(info.b)
% ff=[ff;info.b(i).pnx];
% ff1=[ff1;info.b(i).pny];
% end
% figure;plot3(ff,ff1,SFrame:fr-1)
% legend(a)
% zlabel('Time  ' );
% ylabel('py  ' );
% xlabel('px  ' );

ff=[info.b.pnx];
figure;plot(ff',SFrame:fr-1)
legend(a)
xlabel('Time  ' );
ylabel('position' );



