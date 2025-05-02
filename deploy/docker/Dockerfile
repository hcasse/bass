FROM bass:base
EXPOSE 8888

# compile binaries
COPY 	./armv5t/	/bass/armv5t/
WORKDIR	/bass/armv5t
RUN		make install

# copy applications
ADD tmp/bass/bass		/bass/bass
ADD tmp/bass/orchid		/bass/orchid
ADD tmp/bass/assets		/bass/assets
#COPY tmp/bass/*.so		/bass/
COPY tmp/bass/*.ini		/bass/
#ADD tmp/bass/data		/bass/data

# command to launch
WORKDIR /bass
ENV PYTHONPATH /bass
ENV PYTHONUNBUFFERED=1
CMD python3 -m bass.server --debug --verbose
