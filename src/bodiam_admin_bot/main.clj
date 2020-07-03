(ns bodiam-admin-bot.main
  (:require [discljord.connections :as c]
            [discljord.messaging :as m]
            [discljord.events :as e]
            [clojure.core.async :as a]
            [clojure.string :as string]
            [clojure.java.io :as io])
  (:gen-class))

(def token "NzI4NzMwODg0OTU3NjY3MzI4.Xv-qiw.6iUwTQEvBZJHCxcB-1XAG40VJPg")
(def state (atom nil))
(def banned-artists (atom nil))

(defn create-dm [author-id content]
  (let [{:keys [id] :as dm-channel} @(m/create-dm! (:messaging @state) author-id)]
    (m/create-message! (:messaging @state) id :content content)))

(defn list-banned-artists [{:keys [id]}]
  (->> (string/join "\n" @banned-artists)
       (format "Blacklisted artists: ```\n%s\n```")
       (create-dm id)))

(defn get-blacklisted-artist [content]
  (some #(when (string/includes? content %) %) @banned-artists))

;(defn add-artist-blacklist )

(defn send-warning-dm [blacklisted-artist {:keys [id]}]
  (let [warning-message (format "Your message has been deleted as it contained a link to an artist blacklisted on the server - `%s` (to see a full list of blacklisted artists on the server, use !listartistblacklist)" blacklisted-artist)]
    (create-dm id warning-message)))

(defmulti handle-event
  (fn [event-type event-data]
    event-type))

(defmethod handle-event :default
  [event-type event-data])

(defmethod handle-event :message-create
  [event-type {{bot :bot} :author :keys [id author channel-id content] :as message}]
  (let [delete-message (fn [] (m/delete-message! (:messaging @state) channel-id id))]
    (cond
      (string/includes? content "!listartistblacklist") (do
                                                          (delete-message)
                                                          (list-banned-artists author))
      (and (string/includes? content "twitter")
           (get-blacklisted-artist content))
      (do
        (delete-message)
        (send-warning-dm (get-blacklisted-artist content) author)))))

(defn -main
  [& args]
  (let [event-ch (a/chan 100)
        connection-ch (c/connect-bot! token event-ch)
        messaging-ch (m/start-connection! token)
        init-state {:connection connection-ch
                    :event event-ch
                    :messaging messaging-ch}
        banned-artists-list (-> (slurp "./banned-artists.txt")
                                (string/split-lines))]
    (reset! state init-state)
    (reset! banned-artists banned-artists-list)
    (e/message-pump! event-ch handle-event)
    (m/stop-connection! messaging-ch)
    (c/disconnect-bot! connection-ch)))

(-main)
