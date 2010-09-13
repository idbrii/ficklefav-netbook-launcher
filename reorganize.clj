(import '(javax.swing JFrame JLabel JButton JPanel)
        '(java.awt.event ActionListener)
        '(javax.imageio ImageIO)
        '(java.io File)
        '(java.awt GridBagLayout GridBagConstraints Color Font RenderingHints))

(defn create-model [] (ref "Useless data"))

(defn create-image [filename]
  (let
    [img (ImageIO/read (File. filename))]
    (proxy [JPanel] []
      (paint [g]
             (doto g
               ; just draw it!
               (.drawImage img 0 0 nil))))))

(defn create-graphics-panel [model]
  (let [panel
        (proxy [JPanel] []
          (paint [g]
                 (doto g
                   ;clear the background
                   (.setColor (. Color black))
                   (.fillRect 0 0 (.getWidth this) (.getHeight this))

                   ;draw the text
                   (.setRenderingHint (. RenderingHints KEY_ANTIALIASING)
                                      (. RenderingHints VALUE_ANTIALIAS_ON))
                   (.setFont (Font. "Serif" (. Font PLAIN) 40))
                   (.setColor (. Color white))
                   (.drawString @model 20 40))))]

    ;repaint when the model changes
    (add-watch model "repaint" (fn [k r o n] (.repaint panel)))
    panel))

(defn create-gui-panel [model]
  (defn create-image-constraints []
    (let [c (GridBagConstraints.)]
      (set! (.fill c) (. GridBagConstraints BOTH))
      (set! (.gridx c) 1)
      (set! (.weightx c) 10)
      c))

  (defn create-panel-constraints []
    (let [c (GridBagConstraints.)]
      (set! (.gridy c) 1)
      (set! (.weighty c) 1)
      (set! (.fill c) (. GridBagConstraints BOTH))
      c))

  (let [gridbag (GridBagLayout.)
        image1 (create-image "/usr/share/icons/Faenza/apps/32/AdobeReader.png")
        image2 (create-image "/usr/share/icons/Faenza/apps/32/Thunar.png")
        image3 (create-image "/usr/share/icons/Faenza/apps/48/WorldOfGoo.png")
        ;panel (create-graphics-panel model)
        ]
    ;set up the gridbag constraints
    (doto gridbag
      (.setConstraints image1 (create-image-constraints))
      (.setConstraints image2 (create-image-constraints))
      (.setConstraints image3 (create-image-constraints))
      ;(.setConstraints panel (create-panel-constraints))
      )
    ;add the components to the panel and return it
    (doto (JPanel.)
      (.setLayout gridbag)
      (.add image1)
      (.add image2)
      (.add image3)
      ;(.add panel)
      )))

  (defn show-in-frame [panel width height frame-title]
    (doto (JFrame. frame-title)
      (.add panel)
      (.setSize width height)
      (.setVisible true)))

  (show-in-frame
    (create-gui-panel (create-model))
    400
    400
    "reorganizer")
