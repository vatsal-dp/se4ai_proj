package demo;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class ODFlakeTest {
    private static int x = 0;

    @Test
    public void polluted() {
        assertEquals(0, x);
    }

    @Test
    public void polluter() {
        x = 1;
        assertEquals(1, x);
    }
}
