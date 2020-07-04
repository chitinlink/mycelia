# bodiamadminbot

The Bodiam Admin Bot is (currently) written using **Clojure**, with the [discljord](https://github.com/IGJoshua/discljord) library. 

## Prerequisites

For local development, one will need the following:
* A version of the JDK - (Primarily using Java 11).
* Basic clojure tooling, in particular [Leiningen](https://leiningen.org/)

## Building/Running a JAR

To build a jar from the root of the folder, you can use the command `lein uberjar`, and the JAR is generated within the `target/` folder. 

When running the JAR, you must ensure it is within the same folder as the banned artist/user list.
