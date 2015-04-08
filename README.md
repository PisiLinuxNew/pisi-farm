# pisi-farm
Next generation pisi farm system

##Abstract
Current farm system that builds the packages for the PisiLinux distribution have some shortcomings. This new approach 
will provide us more functionality, like allowing volunteers to compile individual packages on their own systems in  chrooted environment, or in a docker container.

There are a lot of work to be done to complete this project. 

We have to provide recipes for specific package groups, where you have to follow specific orders to compile that package groups.

##Requirements
We need a web hook for github repository. By setting this hook, github will send the details of push to the url we specified about the push operations.
