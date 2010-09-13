import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;

public class Scratch {
    public static void main (String[] args)
    {
        loadImage("/usr/share/icons/Faenza/apps/16/AdobeReader.png");
    }
    public static BufferedImage loadImage(String ref) {  
        BufferedImage bimg = null;  
        try {  

            File f = new File(ref);
            System.out.println(f);
            bimg = ImageIO.read(f);  
            System.out.println(bimg);
        } catch (Exception e) {  
            e.printStackTrace();  
        }  
        return bimg;  
    }  
}
